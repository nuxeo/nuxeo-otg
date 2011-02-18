from notg.storage import Info

class Synchronizer(object):
    """Utility to compare abstract filesystem trees and update the storage

    The synchronizer is in charge of introspecting the trees, updating
    the metadata in the storage, compute the list of synchronization
    operations and perform the file transfers.
    """

    def __init__(self, storage, local_client, remote_client):
        self.storage = storage
        self.local_client = local_client
        self.remote_client = remote_client

        self.binding = self.storage.get_binding(local_client.base_folder)
        if self.binding is None:
            self.binding = self.storage.add_binding(
                local_client.base_folder, remote_client.base_folder,
                getattr(remote_client, 'repository_url', None),
                getattr(remote_client, 'username', None),
                getattr(remote_client, 'password', None))

    def get_operations(self):
        """Returns list of operations needed to bring both trees in sync."""
        pass

    def update_local_info(self):
        new_infos = self.local_client.get_descendants()
        self.storage.update_states(self.binding, new_infos, 'local')

    def update_remote_info(self):
        new_infos = self.remote_client.get_descendants()
        self.storage.update_states(self.binding, new_infos, 'remote')

    #
    # Basic update operations
    #
    def push(self, path):
        self.log("Pushing object with path: %s" % path)
        state = self.local_client.get_state(path)
        if state.type == 'folder':
            self.remote_client.mkdir(path)
        else:
            content = self.local_client.get_content(path)
            self.remote_client.mkfile(path, content)

    def pull(self, path):
        self.log("Pulling object with path: %s" % path)
        state = self.remote_client.get_state(path)
        if state.type == 'folder':
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
