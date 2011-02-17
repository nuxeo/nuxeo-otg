import random
import unittest
import tempfile
from unittest.case import skip
from notg.client import LocalClient, RemoteClient

LOCAL_PATH = "/tmp"

ROOT = "http://cmis.demo.nuxeo.org/nuxeo/atom/cmis"
REMOTE_PATH = "/default-domain"
USERNAME = PASSWORD = "Administrator"


class AbstractClientTest(unittest.TestCase):
    __test__ = False
    client = None

    def test_mkdir(self):
        temp_dir_name = self.random_name()
        self.client.mkdir(temp_dir_name)
        self.client.delete(temp_dir_name)

    def test_mkfile(self):
        temp_file_name = self.random_name()
        self.client.mkfile(temp_file_name)
        self.client.delete(temp_file_name)

    def test_update(self):
        temp_file_name = self.random_name()
        self.client.mkfile(temp_file_name)
        self.client.delete(temp_file_name)

    def random_name(self):
        return "test-%d" % random.randint(0, 1000000)


class LocalClientTest(AbstractClientTest):
    __test__ = True

    def setUp(self):
        self.client = LocalClient(LOCAL_PATH)


class RemoteClientTest(AbstractClientTest):
    __test__ = True

    def setUp(self):
        self.client = RemoteClient(ROOT, USERNAME, PASSWORD, REMOTE_PATH)

