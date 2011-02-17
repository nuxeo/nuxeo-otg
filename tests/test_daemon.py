import unittest
from notg.daemon import Daemon
from notg.client import Client
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join
from os import listdir

REPO_URL = "http://cmis.demo.nuxeo.org/nuxeo/atom/cmis"
BASE_FOLDER = "/default-domain/workspaces/"

TEST_WORKSPACE = "test-workspace"

USERNAME = 'Administrator'
PASSWORD = 'Administrator'


class DaemonTest(unittest.TestCase):

    def setUp(self):
        # syncronization daemon
        self.daemon = Daemon(monitor=False)

        # local document to synchronise
        self.local_folder = mkdtemp()

        # direct access to the server to simulate user creating / updating /
        # deleting content on the repository directly
        self.client = Client(REPO_URL, USERNAME, PASSWORD, BASE_FOLDER)

        if self.client.exists(TEST_WORKSPACE):
            self.client.delete(TEST_WORKSPACE)

        self.client.create(TEST_WORKSPACE, 'Workspace')

        # attache the local and remote folders
        self.daemon.attach(self.local_folder, REPO_URL,
                           BASE_FOLDER + TEST_WORKSPACE,
                           username=USERNAME, password=PASSWORD)

    def tearDown(self):
        rmtree(self.local_folder)
        self.client.delete(TEST_WORKSPACE)
        self.daemon.clear_storage()

    def test_create_one_local_file(self):
        d = self.daemon

        # the remote workspace is empty, as is the local folder: nothing to do
        self.assertEqual(len(d.pending_operations()), 0)

        # the local user drop a text file
        with open(join(self.local_folder, 'file_1.txt'), 'wb') as f:
            f.write("This is the content of a text file.\n")

        # recompute the diff
        self.assertEqual(len(d.pending_operations()), 1)

        # synchronize with server
        d.synchronize(async=False)
        self.assertEqual(len(d.pending_operations()), 0)

        # check content on server
        c = self.client
        children = c.get_children(TEST_WORKSPACE)
        self.assertEqual(len(children), 1)

        self.assertEqual(children[0].name, 'file_1.txt')
        self.assertEqual(children[0].get_content().read(),
                         "This is the content of a text file.\n")

    def test_create_one_remote_file(self):
        d = self.daemon
        self.assertEqual(len(d.pending_operations()), 0)

        # the users create a set a of new file on the server
        c = self.client
        c.create_file(TEST_WORKSPACE + '/file_1.txt',
                      content='This is the content of the server file.\n')

        # one operation to perform
        self.assertEqual(len(d.pending_operations()), 1)

        # trigger the sync
        d.synchronize(async=False)
        self.assertEqual(len(d.pending_operations()), 0)

        # check content on local filesystem
        local_files = listdir(self.local_folder)
        self.assertEqual(local_files, ['file_1.txt'])

        with open(local_files[0], 'r') as f:
            self.assertEqual(
                f.read(), 'This is the content of the server file.\n')

