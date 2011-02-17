
from notg.storage import Storage
import os

class Controller(object):
    """Main public API for user level operations

    Main operations:
      - create metadata store if missing
      - launch / stop synchronizer process
      - list attach local folder to remote folder
      - query synchronization states of elements
      - query the operation log
      - manually trigger refresh (sync operations)

    All operations performed by the controller are fast and asynchronous:
    the controller never waits for a remote network connection. All
    operations are queued in the shared store to be performed by the
    synchronizer process.
    """

    def __init__(self, monitor=True, storage=None):
        self.monitor = monitor

        # where to persist the current bindings
        if storage is None or isinstance(storage, basestring):
            self.storage = Storage(storage)
        else:
            self.storage = storage

        # TODO: check if synchronizer process is live

    def start_syncronizer(self):
        pass

    def stop_synchronizer(self):
        pass

    def attach(self, local_folder, remote_folder, repository_url=None,
               username=None, password=None):
        self.storage.add_binding(local_folder, remote_folder,
                                 repository_url=repository_url,
                                 username=username, password=password)

    def list_bindings(self):
        pass

    def detach(self, local_folder):
        pass

    def split_path(self, local_path):
        """Return binding and relative path for a local absolute path

        If no matching binding is found raise ValueError
        """
        local_path = os.path.abspath(local_path)
        b = self.storage.get_binding(local_path)
        if b is None:
            raise ValueError("'%s' is not bound to any repository" % local_path)
        return b, local_path[len(b.local_folder) + 1:]

    def status(self, local_folder):
        """Highlevel text status reflecting the local state"""
        binding, path = self.split_path(local_folder)
        return self.storage.get_state(binding, path).local_state

    def refresh(self, local_folder=None, async=True):
        pass

