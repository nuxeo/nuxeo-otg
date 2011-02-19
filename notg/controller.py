import os
import logging

from notg.storage import Storage
from notg.synchronizer import Synchronizer

class Controller(object):
    """Main public API for user level operations.

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

    def attach(self, local_folder, remote_folder, repository_url=None,
               username=None, password=None):
        self.storage.add_binding(local_folder, remote_folder,
                                 repository_url=repository_url,
                                 username=username, password=password)

    def list_bindings(self):
        return self.storage.list_bindings()

    def detach(self, local_folder):
        # TODO: implement me
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

    def status(self, local_folders=[]):
        """High level text status reflecting the local state"""
        summaries = {
            # regular cases
            ('unknown', 'unknown'): 'unknown',
            ('synchronized', 'synchronized'): 'synchronized',
            ('created', 'unknown'): 'locally_created',
            ('unknown', 'created'): 'remotely_created',
            ('modified', 'synchronized'): 'locally_modified',
            ('synchronized', 'modified'): 'remotely_modified',
            ('deleted', 'synchronized'): 'locally_deleted',
            ('synchronized', 'deleted'): 'remotely_deleted',
            ('deleted', 'deleted'): 'deleted', # should never happen

            # conflict cases
            ('modified', 'deleted'): 'conflicted',
            ('deleted', 'modified'): 'conflicted',
            ('modified', 'modified'): 'conflicted',
        }
        results = []
        for binding, path in self.get_bindings_and_path_for(local_folders):
            cs = self.storage.get_state(binding, path)

            summary = summaries.get((cs.local_state, cs.remote_state))
            if summary is None:
                logging.warn("unexpected compound state: %s", cs)
                summary = 'unknown'
            results.append((binding.local_folder, path, summary))
        return results

    def get_bindings_for(self, local_folders=[]):
        if not local_folders:
            return self.list_bindings()
        else:
            return [self.split_path(folder)[0] for folder in local_folders]

    def get_bindings_and_path_for(self, local_folders=[]):
        pairs = []
        if not local_folders:
            # exhaustive scan
            for b in self.storage.list_bindings():
                for p in sorted(self.storage.get_states(b).keys()):
                    pairs.append((b, p))
        else:
            for local_folder in local_folders:
                pairs.append(self.split_path(local_folder))
        return pairs

    def refresh(self, local_folders=[], async=True):
        bindings = self.get_bindings_for(local_folders)
        if async:
            # TODO queue a command to synchronizer process
            pass
        else:
            # perform synchronization right away
            for b in bindings:
                sync = Synchronizer(self.storage, binding=b)
                sync.update_local_info(updated_other=False)
                sync.update_remote_info(updated_other=True)

    def synchronize(self, local_folders=[], async=True):
        bindings = self.get_bindings_for(local_folders)
        if async:
            # TODO queue a command to synchronizer process
            pass
        else:
            # perform synchronization right away
            for b in bindings:
                sync = Synchronizer(self.storage, binding=b)
                sync.synchronize_all()

