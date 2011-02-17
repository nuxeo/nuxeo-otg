import unittest
from notg.controller import Controller
from notg.client import LocalClient
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join
from os import listdir


class ControllerTest(unittest.TestCase):

    def setUp(self):
        # controller component to test
        self.storage_folder = mkdtemp()
        self.controller = Controller(storage=self.storage_folder,
                                     monitor=False)

        # document trees to synchronize:
        self.local_folder = mkdtemp()
        self.remote_folder = mkdtemp()

        # attach the local and remote folders
        self.controller.attach(self.local_folder, self.remote_folder)

    def tearDown(self):
        rmtree(self.storage_folder)
        rmtree(self.local_folder)
        rmtree(self.remote_folder)
        self.controller.clear_storage()

    def test_create_one_local_file(self):
        ctl = self.controller

        # the remote workspace is empty, as is the local folder: nothing to do
        self.assertEqual(len(ctl.pending_operations()), 0)

        # the local user drop a text file
        with open(join(self.local_folder, 'file_1.txt'), 'wb') as f:
            f.write("This is the content of a text file.\n")


