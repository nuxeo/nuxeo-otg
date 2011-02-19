import unittest
from notg.controller import Controller
from notg.client import LocalClient
from tempfile import mkdtemp
from shutil import rmtree
from os.path import exists
from os.path import join
import time

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
        self.previous_cwd = os.getcwd()
        os.chdir(self.local_folder)

    def tearDown(self):
        os.chdir(self.previous_cwd)
        rmtree(self.storage_folder)
        rmtree(self.local_folder)
        rmtree(self.remote_folder)

    def test_split_path(self):
        ctl = self.controller

        # subfolder of the attachment
        bound_local_abspath = join(
            self.local_folder, 'some_folder', 'some_file')
        binding, path = ctl.split_path(bound_local_abspath)
        self.assertEqual(binding.local_folder, self.local_folder)
        self.assertEqual(binding.remote_folder, self.remote_folder)
        self.assertEqual(path, join('some_folder', 'some_file'))

        # unbound path (outside of the attachment)
        self.assertRaises(ValueError, ctl.split_path, '/somewhere/else')

    def test_state_outside_attached_folder(self):
        ctl = self.controller
        self.assertRaises(ValueError, ctl.status, '/somewhere/else')

    def test_synchronize_one_file(self):
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
        self.assertEqual(ctl.status('file_1.txt'), 'locally_created')

        # launch the synchronization and wait for the result
        ctl.synchronize(async=False)
        self.assertEqual(ctl.status('file_1.txt'), 'synchronized')

        # check that the file has been created
        self.assert_(exists(join(self.remote_folder, 'file_1.txt')))
        with open(join(self.remote_folder, 'file_1.txt'), 'rb') as f:
            self.assertEqual(f.read(), 'This is the content of a text file.\n')

        # edit the view on the remote folder
        remote_file_path = join(self.remote_folder, 'file_1.txt')

        time.sleep(0.1)
        with open(remote_file_path, 'wb') as f:
            f.write("Changed content of the text file.\n")

        # refresh the state
        self.assertEqual(ctl.status('file_1.txt'), 'synchronized')
        ctl.refresh(async=False)
        self.assertEqual(ctl.status('file_1.txt'), 'remotely_modified')

        # synchronize
        ctl.synchronize(async=False)
        self.assertEqual(ctl.status('file_1.txt'), 'synchronized')

        # check that the content has been updated
        with open(join(self.remote_folder, 'file_1.txt'), 'rb') as f:
            self.assertEqual(f.read(), 'Changed content of the text file.\n')

        # delete the local file
        os.unlink(join(self.local_folder, 'file_1.txt'))
        ctl.refresh(async=False)
        self.assertEqual(ctl.status('file_1.txt'), 'locally_deleted')

        # propagate the delete
        ctl.synchronize(async=False)
        self.assert_(not exists(join(self.remote_folder, 'file_1.txt')))


    def test_synchronize_folders(self):
        ctl = self.controller

        # create some folders locally and remotely
        l = self.local_folder
        r = self.remote_folder
        os.makedirs(join(l, 'a', 'b', 'c', 'd'))
        os.makedirs(join(r, 'x', 'y', 'z'))

        # refresh state and check some status
        ctl.refresh(async=False)
        self.assertEqual(ctl.status('a'), 'locally_created')
        self.assertEqual(ctl.status('a/b'), 'locally_created')
        self.assertEqual(ctl.status('a/b/c'), 'locally_created')
        self.assertEqual(ctl.status('a/b/c/d'), 'locally_created')
        self.assertEqual(ctl.status('x'), 'remotely_created')
        self.assertEqual(ctl.status('x/y'), 'remotely_created')
        self.assertEqual(ctl.status('x/y/z'), 'remotely_created')

        # trigger the sync
        ctl.synchronize(async=False)
        self.assertEqual(ctl.status('a'), 'synchronized')
        self.assertEqual(ctl.status('a/b'), 'synchronized')
        self.assertEqual(ctl.status('a/b/c'), 'synchronized')
        self.assertEqual(ctl.status('a/b/c/d'), 'synchronized')
        self.assertEqual(ctl.status('x'), 'synchronized')
        self.assertEqual(ctl.status('x/y'), 'synchronized')
        self.assertEqual(ctl.status('x/y/z'), 'synchronized')

        # check that this is really the case
        self.assert_(os.path.isdir(join(r, 'a', 'b', 'c', 'd')))
        self.assert_(os.path.isdir(join(l, 'x', 'y', 'z')))

        # the local user a text file in remote folder
        with open(join(r, 'a', 'b', 'c', 'file_1.txt'), 'wb') as f:
            f.write("This is the content of a text file.\n")

        # refresh and check status
        ctl.refresh(async=False)
        self.assertEqual(ctl.status('a/b/c'), 'synchronized')
        self.assertEqual(ctl.status('a/b/c/d'), 'synchronized')
        self.assertEqual(ctl.status('a/b/c/file_1.txt'), 'remotely_created')

        # sync the file and check the result in the local folder
        ctl.synchronize(async=False)
        self.assertEqual(ctl.status('a/b/c/file_1.txt'), 'synchronized')
        self.assert_(os.path.isfile(join(l, 'a', 'b', 'c','file_1.txt')))

        # delete the folder c in the local folder and the y folder remotely
        rmtree(join(l, 'a', 'b', 'c'))
        rmtree(join(r, 'x', 'y'))

        # refresh and check the state
        ctl.refresh(async=False)
        self.assertEqual(ctl.status('a'), 'synchronized')
        self.assertEqual(ctl.status('a/b'), 'synchronized')
        self.assertEqual(ctl.status('a/b/c'), 'locally_deleted')
        self.assertEqual(ctl.status('a/b/c/d'), 'locally_deleted')
        self.assertEqual(ctl.status('a/b/c/file_1.txt'), 'locally_deleted')
        self.assertEqual(ctl.status('x'), 'synchronized')
        self.assertEqual(ctl.status('x/y'), 'remotely_deleted')
        self.assertEqual(ctl.status('x/y/z'), 'remotely_deleted')

        # launch the sync, check status and check folder content
        ctl.synchronize(async=False)
        self.assertEqual(ctl.status('a'), 'synchronized')
        self.assertEqual(ctl.status('a/b'), 'synchronized')
        self.assertEqual(ctl.status('a/b/c'), 'unknown')
        self.assertEqual(ctl.status('a/b/c/d'), 'unknown')
        self.assertEqual(ctl.status('a/b/c/file_1.txt'), 'unknown')
        self.assertEqual(ctl.status('x'), 'synchronized')
        self.assertEqual(ctl.status('x/y'), 'unknown')
        self.assertEqual(ctl.status('x/y/z'), 'unknown')

        self.assert_(not exists(join(l, 'a', 'b', 'c')))
        self.assert_(not exists(join(r, 'a', 'b', 'c')))
        self.assert_(not exists(join(l, 'x', 'y')))
        self.assert_(not exists(join(r, 'x', 'y')))



