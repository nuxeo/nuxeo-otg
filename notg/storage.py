
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

    def __repr__(self):
        return "Info(%r, %r, %r, %r, %r)" % (
            self.path, self.uid, self.type, self.mtime, self.digest)


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
