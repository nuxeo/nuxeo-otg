"""Clients implement a defined set of operations.

"""
import shutil
import os
from cmislib.model import CmisClient

class Client(object):
    """Interface for clients."""

    def get_tree(self):
        pass

    # Getters
    def get_info(self, path):
        pass

    def get_stream(self, path):
        """Returns file content (stream) as a string. Fix later."""
        pass

    def get_children(self, path):
        pass

    # Modifiers
    def mkdir(self, path):
        """Creates a directory or folder like object."""
        pass

    def mkfile(self, path, content=None):
        """Creates a file-like object. Fill it with content if needed."""
        pass

    def update(self, path, content):
        """Updates existing object with provided content and/or metadata."""
        pass

    def delete(self, path):
        """Deletes object (recursively, if this is a folder."""
        pass



class LocalClient(Client):

    def __init__(self, root):
        self.root = root

    def get_tree(self):
        pass

    # Getters
    def get_info(self, path):
        fd = open(os.path.join(self.root, path), "wcb")

        pass

    def get_stream(self, path):
        fd = open(os.path.join(self.root, path), "b")
        return fd.read()

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
        fd = open(os.path.join(self.root, path), "wb")
        fd.write(content)
        fd.close()

    def delete(self, path):
        os_path = os.path.join(self.root, path)
        if os.path.isfile(os_path):
            os.unlink(os_path)
        else:
            shutil.rmtree(os_path)


class RemoteClient(Client):
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

    def mkfile(self, path, content=None):
        pass

    def delete(self, path):
        remotePath = self.base_folder + path
        object = self.remote_repo.getObjectByPath(remotePath)
        # XXX: hack, fix later
        try:
            object.delete()
        except:
            object.deleteTree()
