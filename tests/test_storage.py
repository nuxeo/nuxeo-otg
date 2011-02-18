from tempfile import mkdtemp
import unittest
from notg.storage import Storage

class StorageTest(unittest.TestCase):

    def setUp(self):
        # controller component to test
        self.storage_folder = mkdtemp('nuxeo-otg-storage-')
        self.storage = Storage(self.storage_folder)

        # document trees to synchronize:
        self.local_folder = mkdtemp(prefix='nuxeo-otg-local-')
        self.remote_folder = mkdtemp(prefix='nuxeo-otg-remote-')

        self.storage.add_binding(self.local_folder, self.remote_folder)


    def test_binding(self):
        self.assertEquals(1, len(self.storage.list_bindings()))
