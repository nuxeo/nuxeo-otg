import random
import shutil
import tempfile
import unittest
from notg.client import LocalClient, RemoteClient
from notg.synchronizer import Synchronizer


class SynchronizerTest(unittest.TestCase):

    def setUp(self):
        self.tempdir1 = tempfile.mkdtemp()
        self.tempdir2 = tempfile.mkdtemp()

        self.local_client = LocalClient(self.tempdir1)
        self.remote_client = LocalClient(self.tempdir2)
        self.synchronizer = Synchronizer(self.local_client, self.remote_client)

    def tearDown(self):
        shutil.rmtree(self.tempdir1)
        shutil.rmtree(self.tempdir2)

    def test_synchronize_file(self):
        TEST_CONTENT = "Some random text"
        self.local_client.mkfile("toto", TEST_CONTENT)
        self.synchronizer.push("toto")
        content = self.remote_client.get_content("toto")
        self.assertEquals(TEST_CONTENT, content)
