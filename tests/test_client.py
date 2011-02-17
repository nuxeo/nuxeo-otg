import unittest
from unittest.case import skip
from notg.client import LocalClient, RemoteClient

ROOT = "http://localhost:8080/nuxeo"
PATH = "/tmp"
USERNAME = PASSWORD = "Administrator"


class AbstractClientTest(unittest.TestCase):
    __test__ = False

    def test(self):
        raise "Error"


class LocalClientTest(AbstractClientTest):
    __test__ = True

    def setUp(self):
        self.client = LocalClient(PATH)


class RemoteClientTest(AbstractClientTest):
    __test__ = True

    def setUp(self):
        self.client = RemoteClient(ROOT, USERNAME, PASSWORD, PATH)

