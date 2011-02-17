import unittest
from unittest.case import skip
from notg.client import LocalClient, RemoteClient

ROOT = "http://localhost:8080/nuxeo"
PATH = "/tmp"
USERNAME = PASSWORD = "Administrator"


class ClientTest(unittest.TestCase):

    def test(self):
        raise "Error"


class LocalClientTest(ClientTest):

    def setUp(self):
        self.client = LocalClient(PATH)


class RemoteClientTest(ClientTest):

    def setUp(self):
        self.client = RemoteClient(ROOT, USERNAME, PASSWORD, PATH)


#def suite():
#    suite1 = unittest.TestLoader().loadTestsFromTestCase(LocalClientTest)
#    suite2 = unittest.TestLoader().loadTestsFromTestCase(RemoteClientTest)
#    return unittest.TestSuite([suite1, suite2])

#if __name__ == '__main__':
#    unittest.TextTestRunner(verbosity=2).run(suite)
