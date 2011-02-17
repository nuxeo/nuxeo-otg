#!env/bin python

"""sync: synchronize with remote CMIS server

"""

import os, time, sys, shutil
#import pyfsevents

from os.path import join, relpath, split, exists
from cmislib.model import CmisClient
from cmislib.exceptions import ObjectNotFoundException 

debug = False
                         
# Constants
class SettingsNuxeo:
    LOCAL_ROOT = os.environ["HOME"] + "/CMIS"
    REMOTE_URL = "http://cmis.demo.nuxeo.org/nuxeo/atom/cmis/"
    #REMOTE_URL = "http://localhost:8080/nuxeo/site/cmis/repository"
    REMOTE_ROOT = "/default-domain"
    LOGIN = PASSWORD = "Administrator"

Settings = SettingsNuxeo


class Node(object):
    """
    Nodes of the tree cache.
    Nodes represent objects (documents or folder) both locally and remotely
    """
    path = None

    # Default values
    local_mtime = 0
    remote_mtime = 0
    has_remote = False
    has_local = False
    deleted_local = False
    deleted_remote = False

    def __init__(self, **args):
        for k, v in args.items():
            setattr(self, k, v)
        # We don't want a malicious server to mess up with parent directories
        print ("Creating node: %s" % self.path).encode('ascii', 'backslashreplace')
        assert self.path.startswith("/")
        assert not "//" in self.path
        assert not "/./" in self.path
        assert not "/../" in self.path
        

class Synchronizer(object):
    
    def __init__(self, local_root, remote_url, remote_root, login, password):
        self.local_root = local_root
        self.remote_url = remote_url
        self.remote_root = remote_root
        self.login = login
        self.password = password
        self.tree = {}
        self.connect()
        
    def connect(self):
        self.client = CmisClient(self.remote_url, self.login, self.password)
        self.remote_repo = self.client.getDefaultRepository()
        self.remote_root_folder = self.remote_repo.getObjectByPath(self.remote_root)
                   
    def updateTree(self):
        self.updateRemoteTree()
        self.updateLocalTree()
        #self.dumpTree()
        
    def dumpTree(self):
        pathList = self.tree.keys()
        pathList.sort()
        for path in pathList:
            node = self.tree[path]
            print node.path, node.has_local, node.has_remote
        print
    
    #
    # Remote tree
    #
    def updateRemoteTree(self):
        result_set = self.remote_root_folder.getDescendants()
        path_list = {}
        for result in result_set.getResults():
            properties = result.getProperties()
            if 1 or debug:
                propNames = properties.keys()
                propNames.sort()
                for propName in propNames:
                    print propName, ":", properties[propName] 
                print
            cmis_path = properties.get("cmis:path")
            if cmis_path is None:
                oid = properties["cmis:objectId"]
                cmis_path = self.getPath(oid)
            path = "/" + relpath(cmis_path, self.remote_root)
            path_list[path] = None
            self.updateRemoteNode(path, properties)
        for path, node in self.tree.items():
            if not path_list.has_key(path):
                node.deleted_remote = True
                
    # Temp hack
    def getPath(self, oid):
        document = self.remote_repo.getObject(oid)

        first_parent = document.getObjectParents()[0]
        path = first_parent.getProperties()["cmis:path"] + "/" + document.getProperties()["cmis:name"]
        return path
    
    def updateRemoteNode(self, path, properties):
        if path not in self.tree:
            self.tree[path] = Node(path=path)
        node = self.tree[path]
        node.has_remote = True
        if properties["cmis:baseTypeId"] == "cmis:folder":
            node.type = "folder"
        else:
            node.type = "document"

    #
    # Local tree
    #
    def updateLocalTree(self, dirPath=None):
        # Find locally deleted objects
        for path, node in self.tree.items():
            if not exists(self.local_root + path):
                node.deleted_local = True                
        # Update from existing files and directories
        if dirPath is None:
            dirPath = self.local_root
        for root, dirs, files in os.walk(dirPath):
            for dn in dirs:
                localPath = join(root, dn)
                path = "/" + relpath(localPath, self.local_root)
                self.updateLocalNode(path, "folder")
            for fn in files:
                localPath = join(root, fn)
                path = "/" + relpath(localPath, self.local_root)
                self.updateLocalNode(path, "document")

    def updateLocalNode(self, path, type):
        print "Updating local %s: %s" % (type, path)
        if path not in self.tree:
            self.tree[path] = Node(path=path)
        node = self.tree[path]
        node.has_local = True
        node.type = type

    #
    # Actual Synchronisation
    #
    def syncTree(self):
        path_list = self.tree.keys()
        path_list.sort()
        for path in path_list:
            node = self.tree[path]
            if node.deleted_local and node.deleted_remote:
                self.deleteNode(node)
            elif node.deleted_local and node.has_remote:
                print "Deleting remote node:", path
                self.deleteRemote(node)
            elif node.deleted_local and node.has_local:
                print "Deleting remote node:", path
                self.deleteLocal(node)
            elif node.has_local and not node.has_remote:
                print "Pushing node:", path
                self.pushNode(node)
            elif node.has_remote and not node.has_local:
                print "Pulling node:", path
                self.pullNode(node)
            else:
                pass
                #print "Ignoring node:", path

    def deleteLocal(self, node):
        print "Deleting local %s" % node.path
        localPath = self.local_root + node.path
        shutil.rmtree(localPath)
        self.deleteNode(node)
        
    def deleteRemote(self, node):
        print "Deleting remote %s" % node.path
        remotePath = self.remote_root + node.path
        object = self.remote_repo.getObjectByPath(remotePath)
        # XXX: hack, fix later
        try:
            object.delete()
        except:
            object.deleteTree()
        self.deleteNode(node)

    def deleteNode(self, node):
        for path in self.tree.keys():
            if path.startswith(node.path):               
                del self.tree[path]

    def pushNode(self, node):
        path = node.path
        remote_path = self.remote_root + path
        local_path = self.local_root + path
        try:
            print "Pushing node: %s to %s" % (local_path, remote_path)
            object = self.remote_repo.getObjectByPath(remote_path)
            print "Object exists, do nothing"
            return
        except ObjectNotFoundException:
            pass

        parent_path, name = split(remote_path)
        parent_folder = self.remote_repo.getObjectByPath(parent_path)
        if node.type == "folder":
            parent_folder.createFolder(name)
        else:
            content = open(local_path, "rb")
            parent_folder.createDocument(name, contentFile=content)
            content.close()
        
    def pullNode(self, node):
        path = node.path
        remote_path = self.remote_root + path
        local_path = self.local_root + path
        print "Pulling node: %s to %s" % (remote_path, local_path)
        if node.type == "folder":
            os.mkdir(local_path)
        else:
            object = self.remote_repo.getObjectByPath(remote_path)
            fd = open(local_path, "wcb")
            fd.write(object.getContentStream().read())

    # Callback for fsevent (Mac OS)
    #def sync(self, path, isrec):
    #    print "Path = %s, isrec = %s" % (path, isrec)
    #    self.push(path)


def main():
    settings = Settings()
    d = {}
    for k in dir(settings):
        if not k.startswith("_"):
            d[k.lower()] = getattr(settings, k)

    s = Synchronizer(**d)

    while True:
        print "Updating tree"
        s.updateTree()
        s.dumpTree()
        print "Syncing"
        #s.syncTree()
        print "Sleeping..."   
        time.sleep(10)
    
    #pyfsevents.registerpath(settings.LOCAL_ROOT, synchronizer.sync)
    #pyfsevents.listen()

if __name__ == "__main__":
    main()
