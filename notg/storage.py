
import os

class Binding(object):

    def __init__(self, local_folder, remote_folder, repository_url, username,
                 password):
        self.local_folder = local_folder
        self.remote_folder = remote_folder
        self.repository_url = repository_url
        self.username = username
        self.password = password

    def __eq__(self, other):
        return (self.local_folder == other.local_folder
                and self.remote_folder == other.remote_folder
                and self.repository_url == other.repository_url
                and self.username == other.username)


class Info(object):
    """Data transfer object representing the state in one tree"""

    def __init__(self, path, uid, type, mtime, digest=None):
        self.path = path
        self.uid = uid
        self.type = type
        self.mtime = mtime
        self.digest = digest


class CompoundState(object):
    """Stored metadata for each tree node to be synchronized"""

    local_state = 'unknown'
    remote_state = 'unknown'
    local_info = None
    remote_info = None

    def __init__(self, binding, path):
        self.binding = binding
        self.path = path

    def get_info(self, tree):
        return getattr(self, tree + '_info')

    def set_info(self, tree, info):
        setattr(self, tree + '_info', info)

    def get_state(self, tree):
        return getattr(self, tree + '_state')

    def set_state(self, tree, state):
        setattr(self, tree + '_state', state)


class Storage(object):
    """Local storage for stateful metadata and interprocess communication"""

    def __init__(self, db_path=None):
        self.bindings = []
        self.states = {}

    def add_binding(self, local_folder, remote_folder, repository_url=None,
                    username=None, password=None):
        local_folder = os.path.abspath(local_folder)
        b = self.get_binding(local_folder)
        if b is not None:
            raise ValueError("Cannot bind '%s' since '%s' is already bound to"
                             " '%s/%s'" % (local_folder, b.local_folder,
                                           b.repository_url, b.remote_folder))

        binding = Binding(local_folder, remote_folder, repository_url,
                          username, password)
        self.bindings.append(binding)
        return binding

    def list_bindings(self):
        return self.bindings[:]

    def get_binding(self, local_path):
        local_path = os.path.abspath(local_path)
        for binding in self.bindings:
            if local_path.startswith(binding.local_folder):
                return binding
        return None

    def get_state(self, binding, path):
        return self.states.get((binding, path), CompoundState(binding, path))

    def set_state(self, binding, path, state):
        self.states[(binding, path)] = state

    def get_states(self, binding):
        return dict((p, s) for (b, p), s in self.states.iteritems()
                    if b == binding)

    def update_states(self, binding, new_infos, tree):
        """Compute the new states based on modification time only"""
        old_states = self.get_states(binding)

        other = 'remote' if tree == 'local' else 'local'

        for new_info in new_infos:
            path = new_info.path

            compound_state = old_states.setdefault(
                path, CompoundState(binding, path))

            old_info = compound_state.get_info(tree)
            other_old_info = compound_state.get_info(other)

            if old_info is None:
                compound_state.set_info(tree, new_info)
                if other_old_info is not None:
                    # this is a first scan after an attachment: assumed
                    # documents are the same by default: this would require
                    # digest access to ensure that this is true. If not true we
                    # sould trigger the conflict resolution mechanism instead
                    compound_state.set_state(tree, 'synchronized')
                    compound_state.set_state(other, 'synchronized')
                else:
                    # leave the state to unknown while waiting for other info to
                    # come in
                    pass
            else:
                # detect modifications to propagate
                if new_info.mtime > old_info.mtime:
                    # this is a modified document
                    compound_state.set_state(tree, 'modified')
                    compound_state.set_info(tree, new_info)

            # save back change to storage
            self.set_state(binding, path, compound_state)

            # remove from the list of collected states to be able to detect
            # deletions
            del old_states[new_info.path]

        # remaining states can be deletions or new file created on the other
        # side
        for path, compound_state in old_states.iteritems():
            if old_info.get(tree) is not None:
                # mark old path no longer present in the tree as deleted
                compound_state.set_state(tree, 'deleted')
                compound_state.set_info(tree, None)
            else:
                # we do not have any old info on this document, this is a
                # new document from the other side
                compound_state.set_info(other, 'created')

            # save the change
            self.set_state(binding, path, compound_state)


