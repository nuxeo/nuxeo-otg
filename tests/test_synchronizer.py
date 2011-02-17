import shutil
import tempfile
import unittest
from cmislib.exceptions import ObjectNotFoundException

from notg.storage import Storage
from notg.client import LocalClient, RemoteClient
from notg.synchronizer import Synchronizer

from config import *

class AbstractSynchronizerTest(unittest.TestCase):
    __test__ = False
    local_client = None
    synchronizer = None
    remote_client = None

    TEST_CONTENT = "Some random text"
    FILE_NAME = "toto"

    def test_synchronize_file(self):
        self.local_client.mkfile(self.FILE_NAME, self.TEST_CONTENT)
        self.synchronizer.push(self.FILE_NAME)
        content = self.remote_client.get_content(self.FILE_NAME)
        self.assertEquals(self.TEST_CONTENT, content)


class LocalLocalSynchronizerTest(AbstractSynchronizerTest):
    __test__ = True

    def setUp(self):
        self.storagedir = tempfile.mkdtemp()
        self.tempdir1 = tempfile.mkdtemp()
        self.tempdir2 = tempfile.mkdtemp()

        self.storage = Storage(self.storagedir)
        self.local_client = LocalClient(self.tempdir1)
        self.remote_client = LocalClient(self.tempdir2)

        self.synchronizer = Synchronizer(
            self.storage, self.local_client, self.remote_client)

    def tearDown(self):
        shutil.rmtree(self.storagedir)
        shutil.rmtree(self.tempdir1)
        shutil.rmtree(self.tempdir2)


class LocalRemoteSynchronizerTest(AbstractSynchronizerTest):
    __test__ = True

    def setUp(self):
        self.storagedir = tempfile.mkdtemp()
        self.storage = Storage(self.storagedir)

        self.tempdir1 = tempfile.mkdtemp()
        self.local_client = LocalClient(self.tempdir1)

        self.remote_client = RemoteClient(ROOT, USERNAME, PASSWORD, REMOTE_PATH)
        try:
            self.remote_client.delete(self.FILE_NAME)
        except ObjectNotFoundException:
            pass

        self.synchronizer = Synchronizer(
            self.storage, self.local_client, self.remote_client)

    def tearDown(self):
        shutil.rmtree(self.storagedir)
        shutil.rmtree(self.tempdir1)
        #try:
        #    self.remote_client.delete(self.FILE_NAME)
        #except ObjectNotFoundException:
        #    pass

