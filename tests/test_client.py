from datetime import datetime
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
        now = datetime.now().replace(microsecond=0)
        name = self.random_name()
        self.client.mkdir(name)

        state = self.client.get_state(name)
        self.assertEquals(name, state.path.split("/")[-1])
        self.assert_(state.mtime >= now)

        self.client.delete(name)

    def test_mkfile(self):
        now = datetime.now().replace(microsecond=0)
        name = self.random_name()
        self.client.mkfile(name, self.TEST_CONTENT)

        state = self.client.get_state(name)
        self.assertEquals(name, state.path.split("/")[-1])
        self.assert_(state.mtime >= now)

        content = self.client.get_content(name)
        self.assertEquals(self.TEST_CONTENT, content)

        self.client.delete(name)

    def test_update(self):
        name = self.random_name()
        self.client.mkfile(name)

        now = datetime.now().replace(microsecond=0)
        self.client.update(name, self.TEST_CONTENT)
        content = self.client.get_content(name)
        self.assertEquals(self.TEST_CONTENT, content)

        state = self.client.get_state(name)
        self.assert_(state.mtime >= now)

        self.client.delete(name)

    def test_get_descendants(self):
        name = self.random_name()
        self.client.mkdir(name)
        self.client.mkdir(name + "/toto1")
        self.client.mkdir(name + "/toto2")
        self.client.mkfile(name + "/toto3")

        descendants = self.client.get_descendants(name)
        self.assertEquals(3, len(descendants))

        self.client.delete(name)

    #
    # Utility functions
    #
    def random_name(self):
        return "test-%d" % random.randint(0, 1000000)


class LocalClientTest(AbstractClientTest):
    __test__ = True

    def setUp(self):
        self.client = LocalClient(LOCAL_PATH)


class RemoteClientTest(AbstractClientTest):
    __test__ = True

    def setUp(self):
        self.client = RemoteClient(REPOSITORY_URL, USERNAME, PASSWORD,
                                   REMOTE_PATH)

