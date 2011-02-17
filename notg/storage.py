
import os

class Binding(object):

    def __init__(self, local_folder, remote_folder, repository_url, username,
                 password):
        self.local_folder = local_folder
        self.remote_folder = remote_folder
        self.repository_url = repository_url
        self.username = username
        self.password = password


class CompoundState(object):

    local_uid = None
    local_state = 'unknown'
    local_mdate = None
    local_digest = None

    remote_uid = None
    remote_state = 'unknown'
    remote_mdate = None
    remote_digest = None

    def __init__(self, binding, path):
        self.binding = binding
        self.path = path


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

    def update_local_states(self, binding, new_states):
        pass

    def update_remote_states(self, binding, new_states):
        pass

