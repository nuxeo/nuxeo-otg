"""Clients implement a defined set of operations.

"""
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
        pass

    def mkfile(self, path):
        pass

    def update(self, path, content):
        pass

    def delete(self, path):
        pass


class RemoteClient(object):
    """CMIS Client"""

    def __init__(self, username, password, base_folder):
        self.url = url
        self.username = username
        self.password = password
        self.base_folder = base_folder

        self.client = CmisClient(url, username, password)
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
