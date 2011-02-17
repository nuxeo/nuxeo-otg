"""Clients implement a defined set of operations.

"""
import os
from cmislib.model import CmisClient

class LocalClient(object):

    def __init__(self, root):
        self.root = root

    def get_tree(self):
        pass

    # Getters
    def get_info(self, path):
        pass

    def get_stream(self, path):
        pass

    def get_children(self, path):
        pass

    # Modifiers
    def mkdir(self, path):
        os.mkdir(os.path.join(self.root, path))

    def mkfile(self, path, content=None):
        fd = open(os.path.join(self.root, path), "wcb")
        if content:
            fd.write(content)
        fd.close()

    def update(self, path, content):
        pass

    def delete(self, path):
        os_path = os.path.join(self.root, path)
        if os.path.isfile(os_path):
            os.unlink(os_path)
        else:
            os.rmdir(os_path)


class RemoteClient(object):
    """CMIS Client"""

    def __init__(self, repo_url, username, password, base_folder):
        self.repo_url = repo_url
        self.username = username
        self.password = password
        self.base_folder = base_folder

        self.client = CmisClient(repo_url, username, password)
        self.remote_repo = self.client.getDefaultRepository()


    def get_tree(self):
        pass

    # Modifiers
    def mkdir(self, path):
        pass

    def mkfile(self, path):
        pass

    def delete(self, path):
        remotePath = self.base_folder + path
        object = self.remote_repo.getObjectByPath(remotePath)
        # XXX: hack, fix later
        try:
            object.delete()
        except:
            object.deleteTree()
