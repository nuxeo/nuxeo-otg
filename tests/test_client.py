import random
import unittest
from notg.client import LocalClient, RemoteClient
from config import *

LOCAL_PATH = "/tmp"


class AbstractClientTest(unittest.TestCase):
    __test__ = False
    client = None

    TEST_CONTENT = "Some content."


    def test_mkdir(self):
        name = self.random_name()
        self.client.mkdir(name)
        info = self.client.get_info(name)
        self.assertEquals(name, info['name'])
        self.client.delete(name)

    def test_mkfile(self):
        name = self.random_name()
        self.client.mkfile(name, self.TEST_CONTENT)

        info = self.client.get_info(name)
        self.assertEquals(name, info['name'])

        content = self.client.get_content(name)
        self.assertEquals(self.TEST_CONTENT, content)

        self.client.delete(name)

    def test_update(self):
        name = self.random_name()
        self.client.mkfile(name)

        self.client.update(name, self.TEST_CONTENT)
        content = self.client.get_content(name)
        self.assertEquals(self.TEST_CONTENT, content)
        self.client.delete(name)

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

    def xxx(self):
        name = self.random_name()
        self.client.mkdir(name)
        self.client.mkdir(name + "/toto1")
        self.client.mkdir(name + "/toto2")
        self.client.mkfile(name + "/toto3")

        self.assertEquals([], self.client.get_descendants(""))

