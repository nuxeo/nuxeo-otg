
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
        pass

    def pull(self, path):
        pass

    def delete_remote(self, path):
        self.remote_client.delete(path)

    def delete_local(self, path):
        self.local_client.delete(path)
