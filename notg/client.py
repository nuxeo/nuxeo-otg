"""Clients implement a defined set of operations.

"""
from StringIO import StringIO
import shutil
import os
from datetime import datetime
from cmislib.model import CmisClient

from storage import Info

class Client(object):
    """Interface for clients."""

    # Getters
    def get_state(self, path):
        """Returns a Info object for the given object."""
        raise NotImplementedError

    def get_content(self, path):
        """Returns file/document content as a string. Fix later to handle streaming."""
        raise NotImplementedError

    def get_descendants(self, path=None):
        raise NotImplementedError

    # Modifiers
    def mkdir(self, path):
        """Creates a directory or folder like object."""
        raise NotImplementedError

    def mkfile(self, path, content=None):
        """Creates a file-like object. Fill it with content if needed."""
        raise NotImplementedError

    def update(self, path, content):
        """Updates existing object with provided content."""
        raise NotImplementedError

    def delete(self, path):
        """Deletes object (recursively, if this is a folder)."""
        raise NotImplementedError


class LocalClient(Client):

    def __init__(self, base_folder):
        self.base_folder = base_folder

    # Getters
    def get_state(self, path):
        os_path = os.path.join(self.base_folder, path)
        if os.path.isdir(os_path):
            type = 'folder'
        else:
            type = 'file'
        stat_result = os.stat(os_path)
        mtime = datetime.fromtimestamp(stat_result.st_mtime)
        uid = str(stat_result.st_ino)
        return Info(os_path[len(self.base_folder) + 1:], uid, type, mtime)

    def get_content(self, path):
        fd = open(os.path.join(self.base_folder, path), "rb")
        return fd.read()

    def get_descendants(self, path=None):
        if path is None:
            os_path = self.base_folder
        else:
            os_path = os.path.join(self.base_folder, path)
        result = []
        for root, dirs, files in os.walk(os_path):
            for dir in dirs:
                path = os.path.join(os_path, dir)
                result.append(self.get_state(path))
            for file in files:
                path = os.path.join(os_path, file)
                result.append(self.get_state(path))
        return result

    # Modifiers
    def mkdir(self, path):
        os.mkdir(os.path.join(self.base_folder, path))

    def mkfile(self, path, content=None):
        fd = open(os.path.join(self.base_folder, path), "wcb")
        if content:
            fd.write(content)
        fd.close()

    def update(self, path, content):
        fd = open(os.path.join(self.base_folder, path), "wb")
        fd.write(content)
        fd.close()

    def delete(self, path):
        os_path = os.path.join(self.base_folder, path)
        if os.path.isfile(os_path):
            os.unlink(os_path)
        else:
            shutil.rmtree(os_path)


class RemoteClient(Client):
    """CMIS Client"""

    def __init__(self, repository_url, username, password, base_folder):
        self.repository_url = repository_url
        self.username = username
        self.password = password
        self.base_folder = base_folder

        self.client = CmisClient(repository_url, username, password)
        self.repo = self.client.getDefaultRepository()

    def get_descendants(self, path=""):
        result = []

        remote_path = self.get_remote_path(path)
        object = self.repo.getObjectByPath(remote_path)

        children = object.getChildren()
        for child in children:
            properties = child.properties
            # Hack around some Nuxeo quirks
            child_name = properties['cmis:name']
            if properties.has_key('cmis:path'):
                child_name = properties['cmis:path'].split('/')[-1]
            if path == "":
                child_path = child_name
            else:
                child_path = path + "/" + child_name

            state = self.make_state(child_path, properties)
            if state.type == 'folder':
                result += [state] + self.get_descendants(child_path)
            else:
                result += [state]

        return result

    def get_state(self, path):
        remote_path = self.get_remote_path(path)
        object = self.repo.getObjectByPath(remote_path)
        properties = object.properties
        return self.make_state(path, properties)

    def get_content(self, path):
        remote_path = self.get_remote_path(path)
        object = self.repo.getObjectByPath(remote_path)
        return object.getContentStream().read()

    # Modifiers
    def mkdir(self, path):
        remote_path = self.get_remote_path(path)
        parent_path, name = os.path.split(remote_path)
        parent_folder = self.repo.getObjectByPath(parent_path)
        parent_folder.createFolder(name)

    def mkfile(self, path, content=None):
        remote_path = self.get_remote_path(path)
        parent_path, name = os.path.split(remote_path)
        parent_folder = self.repo.getObjectByPath(parent_path)
        content_file = StringIO(content)
        parent_folder.createDocument(name, contentFile=content_file)

    def update(self, path, content):
        remote_path = self.get_remote_path(path)
        object = self.repo.getObjectByPath(remote_path)
        content_file = StringIO(content)
        return object.setContentStream(content_file)
        # TODO: manage also mime type

    def delete(self, path):
        remote_path = self.get_remote_path(path)
        object = self.repo.getObjectByPath(remote_path)
        # XXX: hack, fix later
        try:
            object.delete()
        except:
            object.deleteTree()

    #
    # Utilities
    #
    def get_remote_path(self, path):
        if path != "":
            return self.base_folder + "/" + path
        else:
            return self.base_folder

    def make_state(self, path, properties):
        if properties['cmis:baseTypeId'] == 'cmis:folder':
            type = 'folder'
        else:
            type = 'file'
        uid = properties['cmis:objectId']
        mtime = properties['cmis:lastModificationDate']
        return Info(path, uid, type, mtime)
