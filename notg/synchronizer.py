
class Synchronizer(object):

    def __init__(self, local_client, remote_client):
        self.local_client = local_client
        self.remote_client = remote_client


    def get_operations(self):
        """Returns list of operations needed to bring both trees in sync."""
        pass

    def fetch_remote_state(self):
        self.fetch_state(self.remote_client)

    def fetch_local_state(self):
        self.fetch_state(self.local_client)

    def fetch_state(self, client):
        pass

    #
    # Basic update operations
    #
    def push(self, path):
        self.log("Pushing object with path: %s" % path)
        info = self.local_client.get_info(path)
        if info['type'] == 'folder':
            self.remote_client.mkdir(path)
        else:
            content = self.local_client.get_content(path)
            self.remote_client.mkfile(path, content)

    def pull(self, path):
        self.log("Pulling object with path: %s" % path)
        info = self.remote_client.get_info(path)
        if info['type'] == 'folder':
            self.local_client.mkdir(path)
        else:
            content = self.remote_client.get_content(path)
            self.local_client.mkfile(path, content)

    def delete_remote(self, path):
        self.log("Deleting remote object with path: %s" % path)
        self.remote_client.delete(path)

    def delete_local(self, path):
        self.log("Deleting remote object with path: %s" % path)
        self.local_client.delete(path)


    #
    # Utility functions
    #
    def log(self, msg):
        print msg