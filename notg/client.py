"""Clients implement a defined set of operations.

"""
from StringIO import StringIO
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

    def get_content(self, path):
        """Returns file/document content as a string. Fix later to handle streaming."""
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
        os_path = os.path.join(self.root, path)
        info = {}
        if os.path.isdir(os_path):
            info['type'] = 'folder'
        else:
            info['type'] = 'file'
        return info

    def get_content(self, path):
        fd = open(os.path.join(self.root, path), "rb")
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
        self.repo = self.client.getDefaultRepository()


    def get_tree(self):
        pass

    # Modifiers
    def mkdir(self, path):
        abs_path = self.get_abs_path(path)
        parent_path, name = os.path.split(abs_path)
        print parent_path
        parent_folder = self.repo.getObjectByPath(parent_path)
        parent_folder.createFolder(name)

    def mkfile(self, path, content=None):
        abs_path = self.get_abs_path(path)
        parent_path, name = os.path.split(abs_path)
        parent_folder = self.repo.getObjectByPath(parent_path)
        content_file = StringIO(content)
        parent_folder.createDocument(name, contentFile=content_file)

    def delete(self, path):
        abs_path = self.get_abs_path(path)
        object = self.repo.getObjectByPath(abs_path)
        # XXX: hack, fix later
        try:
            object.delete()
        except:
            object.deleteTree()

    def get_abs_path(self, path):
        return self.base_folder + path
