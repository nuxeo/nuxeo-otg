import unittest
from notg.client import Client

ROOT = "http://localhost:8080/nuxeo"
USERNAME = PASSWORD = "Administrator"


class ClientTest(unittest.TestCase):

    def setUp(self):
        self.client = Client(ROOT, USERNAME, PASSWORD)

    def test(self):
        pass


if __name__ == '__main__':
    unittest.main()
