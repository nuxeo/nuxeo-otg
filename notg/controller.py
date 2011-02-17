
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
        if storage is None or isintance(storate, basestring):
            self.storage = Storage(storage)
        else:
            self.storage = storage

        # TODO: check if synchronizer process is live

    def start_syncronizer(self):
        pass

    def stop_syncrhonizer(self):
        pass

    def attach(self, local_folder, repository_url, remote_folder,
               username=None, password=None):
        self.storage.add_binding(local_folder, repository_url, remote_folder,
                                 username=username, password=password)

    def list_bindings(self):
        pass

    def detach(self, local_folder):
        pass

    def state(self, local_folder):
        pass

    def refresh(self, local_folder=None):
        pass


