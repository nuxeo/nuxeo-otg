import unittest
from notg.controller import Controller
from notg.client import LocalClient
from tempfile import mkdtemp
from shutil import rmtree
from os.path import exists
from os.path import join

import os


class ControllerTest(unittest.TestCase):

    def setUp(self):
        # controller component to test
        self.storage_folder = mkdtemp('nuxeo-otg-storage-')
        self.controller = Controller(storage=self.storage_folder,
                                     monitor=False)

        # document trees to synchronize:
        self.local_folder = mkdtemp(prefix='nuxeo-otg-local-')
        self.remote_folder = mkdtemp(prefix='nuxeo-otg-remote-')

        # attach the local and remote folders
        self.controller.attach(self.local_folder, self.remote_folder)

        # cd into the local folder to work intuitively with local path in tests
        os.chdir(self.local_folder)

    def tearDown(self):
        rmtree(self.storage_folder)
        rmtree(self.local_folder)
        rmtree(self.remote_folder)

    def test_split_path(self):
        ctl = self.controller

        # subfolder of the attachment
        bound_local_abspath = self.local_folder + '/some_folder/some_file'
        binding, path = ctl.split_path(bound_local_abspath)
        self.assertEqual(binding.local_folder, self.local_folder)
        self.assertEqual(binding.remote_folder, self.remote_folder)
        self.assertEqual(path, 'some_folder/some_file')

        # unbound path (outside of the attachment)
        self.assertRaises(ValueError, ctl.split_path, '/somewhere/else')

    def test_state_outside_attached_folder(self):
        ctl = self.controller
        self.assertRaises(ValueError, ctl.status, '/somewhere/else')

    def _test_create_one_local_file(self):
        ctl = self.controller

        # check for the status of a file that has never existed
        self.assertEqual(ctl.status('file_1.txt'), 'unknown')

        # the local user drop a text file
        with open(join(self.local_folder, 'file_1.txt'), 'wb') as f:
            f.write("This is the content of a text file.\n")

        # the controller did not refresh it's state hence still no pending
        # operations
        self.assertEqual(ctl.status('file_1.txt'), 'unknown')

        # ask for a status update on the synchronisation state of all files
        # and wait for the result
        ctl.refresh(async=False)

        # the new file has been detected
        self.assertEqual(ctl.status('file_1.txt'), 'new')

        # launch the synchronization and wait for the result
        ctl.synchronize(async=False)
        self.assertEqual(ctl.status('file_1.txt'), 'up-to-date')

        # check that the file has been created
        self.assert_(exists(join(self.remote_folder, 'file_1.txt')))
        with open(join(self.remote_folder, 'file_1.txt'), 'wb') as f:
            self.assertEqual(f.read(), 'This is the content of a text file.\n')

