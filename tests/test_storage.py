from tempfile import mkdtemp
import unittest
import shutil

from notg.storage import Storage


class StorageTest(unittest.TestCase):

    def setUp(self):
        # controller component to test
        self.storage_folder = mkdtemp('nuxeo-otg-storage-')
        self.storage = Storage(self.storage_folder)

        # document trees to synchronize:
        self.local_folder = mkdtemp(prefix='nuxeo-otg-local-')
        self.remote_folder = mkdtemp(prefix='nuxeo-otg-remote-')


    def tearDown(self):
        shutil.rmtree(self.storage_folder)
        shutil.rmtree(self.local_folder)
        shutil.rmtree(self.remote_folder)

    def test_bindings(self):
        storage = self.storage

        # by default the storage is empty
        self.assertEquals(0, len(storage.list_bindings()))

        # add a binding to the storage
        storage.add_binding(self.local_folder, self.remote_folder)
        self.assertEquals(1, len(storage.list_bindings()))

        # reopen the storage from the disk and check that the binding is still
        # present
        storage = Storage(self.storage_folder)
        self.assertEquals(1, len(storage.list_bindings()))

        # TODO: implement and test binding removal

    def test_states(self):
        storage = self.storage

        b = storage.add_binding(self.local_folder, self.remote_folder)
        self.assertEquals(0, len(storage.get_states(b)))

        # create a new state by looking for an unknown path
        s = storage.get_state(b, 'some_file.txt')
        self.assertEquals(s.local_state, 'unknown')
        s.set_state('local', 'created')

        # nothing is saved yet
        self.assertEquals(0, len(storage.get_states(b)))

        # save the new state
        storage.set_state(b, s)
        self.assertEquals(1, len(storage.get_states(b)))

        # open a new storage
        storage = Storage(self.storage_folder)
        self.assertEquals(1, len(storage.get_states(b)))
        s = storage.get_state(b, 'some_file.txt')
        self.assertEquals(s.local_state, 'created')

        # delete the state
        storage.delete_state(b, 'some_file.txt')

        # open a new storage and check that it's empty
        storage = Storage(self.storage_folder)
        self.assertEquals(0, len(storage.get_states(b)))

