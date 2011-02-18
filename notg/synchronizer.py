import logging

from notg.storage import Info
from notg.storage import CompoundState
from notg.client import LocalClient
from notg.client import RemoteClient
from notg.notification import notify


class Synchronizer(object):
    """Utility to compare abstract filesystem trees and update the storage

    The synchronizer is in charge of introspecting the trees, updating
    the metadata in the storage, compute the list of synchronization
    operations and perform the file transfers.
    """

    def __init__(self, storage, local_client=None, remote_client=None,
                 binding=None):
        self.storage = storage

        if binding is not None:
            self.binding = b = binding
            self.local_client = LocalClient(b.local_folder)
            if binding.repository_url is not None:
                self.remote_client = RemoteClient(
                        b.repository_url, b.username, b.password, b.remote_folder)
            else:
                # 'local' remote client to be used for tests only
                self.remote_client = LocalClient(b.remote_folder)

        elif local_client is not None and remote_client is not None:
            self.local_client = local_client
            self.remote_client = remote_client

            self.binding = self.storage.get_binding(local_client.base_folder)
            if self.binding is None:
                self.binding = self.storage.add_binding(
                    local_client.base_folder, remote_client.base_folder,
                    getattr(remote_client, 'repository_url', None),
                    getattr(remote_client, 'username', None),
                    getattr(remote_client, 'password', None))
        else:
            raise ValueError("Either a binding or a clients pair must be"
                             " provided")

    def get_operations(self):
        """Returns list of operations needed to bring both trees in sync"""
        # TODO: implement me!
        return []

    def synchronize_all(self):
        """Perform blocking synchronization"""
        # TODO: refactor me to make it a two stages process to allow for
        # queue-based non-blocking asynchronous processing

        # TODO: simplify deletions: handle sub trees

        states = self.storage.get_states(self.binding).items()

        # sort by path names to create folders before
        states.sort()
        for path, state in states:
            if state.local_state in ('created', 'modified'):
                self.push(path)
            elif state.remote_state in ('created', 'modified'):
                self.pull(path)
            elif state.local_state == 'deleted':
                self.delete_remote(path)
            elif state.remote_state == 'deleted':
                self.delete_local(path)

    def update_local_info(self):
        new_infos = self.local_client.get_descendants()
        self.update_states(new_infos, 'local')

    def update_remote_info(self):
        new_infos = self.remote_client.get_descendants()
        self.update_states(new_infos, 'remote')

    def _update_states(self, new_infos, tree):
        """Compute the new states based on modification time only"""
        old_states = self.storage.get_states(self.binding)

        other = 'remote' if tree == 'local' else 'local'
        logging.info("refreshing state for: %s", tree)

        for new_info in new_infos:
            path = new_info.path

            compound_state = old_states.setdefault(
                path, CompoundState(self.binding, path))

            old_info = compound_state.get_info(tree)
            other_old_info = compound_state.get_info(other)

            if old_info is None:
                if other_old_info is not None:
                    # this is a first scan after an attachment: assumed
                    # documents are the same by default: this would require
                    # digest access to ensure that this is true. If not true we
                    # sould trigger the conflict resolution mechanism instead
                    compound_state.set_info(tree, new_info)
                    compound_state.set_state(tree, 'synchronized')
                    compound_state.set_state(other, 'synchronized')
                else:
                    # leave the state to unknown while waiting for other info to
                    # come in
                    compound_state.set_info(tree, new_info)
            else:
                # detect modifications to propagate
                if new_info.mtime > old_info.mtime:
                    # this is a modified document
                    compound_state.set_state(tree, 'modified')
                    compound_state.set_info(tree, new_info)

            # save back change to storage
            self.storage.set_state(self.binding, path, compound_state)

            # remove from the list of collected states to be able to detect
            # deletions
            del old_states[new_info.path]

        # remaining states can be deletions or new file created on the other
        # side
        for path, compound_state in old_states.iteritems():
            if compound_state.get_info(tree) is not None:
                # mark old path no longer present in the tree as deleted
                compound_state.set_state(tree, 'deleted')
                compound_state.set_info(tree, None)
            else:
                # we do not have any old info on this document, this is a
                # new document from the other side
                compound_state.set_state(other, 'created')

            # save the change
            self.storage.set_state(self.binding, path, compound_state)

    #
    # Basic update operations
    #

    def push(self, path):
        logging.info("Pushing object with path: %s" % path)
        notify("", "Pushing file to server", "with path %s" % path)
        info = self.local_client.get_state(path)

        # transfer the content
        if info.type == 'folder':
            self.remote_client.mkdir(path)
        else:
            content = self.local_client.get_content(path)
            self.remote_client.mkfile(path, content)

        # update the metadata
        state = self.storage.get_state(self.binding, path)
        state.set_state('local', 'synchronized')
        state.set_state('remote', 'synchronized')
        new_info = self.remote_client.get_state(path)
        state.set_info('remote', new_info)
        self.storage.set_state(self.binding, path, state)

    def pull(self, path):
        logging.info("Pulling object with path: %s" % path)
        notify("", "Pulling file from server", "with path %s" % path)

        info = self.remote_client.get_state(path)

        # transfer the content
        if info.type == 'folder':
            self.local_client.mkdir(path)
        else:
            content = self.remote_client.get_content(path)
            self.local_client.mkfile(path, content)

        # update the metadata
        state = self.storage.get_state(self.binding, path)
        state.set_state('local', 'synchronized')
        state.set_state('remote', 'synchronized')
        new_info = self.local_client.get_state(path)
        state.set_info('local', new_info)
        self.storage.set_state(self.binding, path, state)

    def delete_remote(self, path):
        logging.info("Deleting remote object with path: %s" % path)
        notify("", "Deleting remote file", "with path %s" % path)
        self.remote_client.delete(path)
        self.storage.delete_state(self.binding, state)

    def delete_local(self, path):
        logging.info("Deleting local object with path: %s" % path)
        notify("", "Deleting local file", "with path %s" % path)
        self.local_client.delete(path)
        self.storage.delete_state(self.binding, state)

