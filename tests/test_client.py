import unittest
import tempfile
from unittest.case import skip
from notg.client import LocalClient, RemoteClient

ROOT = "http://localhost:8080/nuxeo"
PATH = "/tmp"
USERNAME = PASSWORD = "Administrator"


class AbstractClientTest(unittest.TestCase):
    __test__ = False
    client = None

    def test_mkdir(self):
        tmpdir = tempfile.mktemp()
        self.client.mkdir(tmpdir)
        self.client.delete(tmpdir)

    def test_mkfile(self):
        tmpfile = tempfile.mktemp()
        self.client.mkfile(tmpfile)
        self.client.delete(tmpfile)

    def test_update(self):
        tmpfile = tempfile.mktemp()
        self.client.mkfile(tmpfile)
        self.client.delete(tmpfile)


class LocalClientTest(AbstractClientTest):
    __test__ = True

    def setUp(self):
        self.client = LocalClient(PATH)


class RemoteClientTest(AbstractClientTest):
    __test__ = False

    def setUp(self):
        self.client = RemoteClient(ROOT, USERNAME, PASSWORD, PATH)

