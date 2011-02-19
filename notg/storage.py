
import os
import logging
from cPickle import load
from cPickle import dump
from cPickle import HIGHEST_PROTOCOL

class Binding(object):

    def __init__(self, local_folder, remote_folder, repository_url, username,
                 password):
        self.local_folder = local_folder
        self.remote_folder = remote_folder
        self.repository_url = repository_url
        self.username = username
        self.password = password

    def __hash__(self):
        return hash("%s::%s::%s" % (
            self.local_folder, self.remote_folder, self.repository_url))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __cmp__(self, other):
        return hash(self).__cmp__(hash(other))


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
        logging.info("store info for '%s/%s': %r" % (tree, self.path, info))
        setattr(self, tree + '_info', info)

    def get_state(self, tree):
        return getattr(self, tree + '_state')

    def set_state(self, tree, state):
        logging.info("mark '%s/%s' as '%s'" % (tree, self.path, state))
        setattr(self, tree + '_state', state)

    def __repr__(self):
        return ('CompoundState with:\n'
                '  local:\t(%r, %r)\n'
                '  remote:\t(%r, %r)' % (
                    self.local_state, self.local_info,
                    self.remote_state, self.remote_info))


class Storage(object):
    """Local storage for stateful metadata and interprocess communication

    This storage implementation is dummy and not scalable at all: loads all
    metadata in memory and does frequent serialization / deserialization using
    the Pickle module. Needs to be rewritten using sqlite and maybe SQLAlchemy
    but it's a good enough model for prototyping the rest of the application and
    identify the key requirements in terms of persistence and interprocess
    communication.
    """

    BINDINGS_FILE = 'bindings.pickle'
    STATES_FILE = 'states.pickle'

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join('~', '.nuxeo-otg')

        db_path = os.path.expanduser(db_path)
        db_path = os.path.abspath(db_path)
        db_path = os.path.normpath(db_path)

        if not os.path.exists(db_path):
            os.makedirs(db_path)

        if not os.path.isdir(db_path):
            raise IOError("%s is not a valid directory" % db_path)

        self.db_path = db_path

        self.bindings_path = os.path.join(db_path, self.BINDINGS_FILE)
        self.states_path = os.path.join(db_path, self.STATES_FILE)

        self.reload_bindings()
        self.reload_states()

    def reload_bindings(self):
        if os.path.exists(self.bindings_path):
            with open(self.bindings_path, 'rb') as f:
                self.bindings = load(f)
        else:
            self.bindings = []

    def reload_states(self):
        if os.path.exists(self.states_path):
            with open(self.states_path, 'rb') as f:
                self.states = load(f)
        else:
            self.states = {}

    def persist_bindings(self):
        with open(self.bindings_path, 'wb') as f:
            dump(self.bindings, f, HIGHEST_PROTOCOL)

    def persist_states(self):
        with open(self.states_path, 'wb') as f:
            dump(self.states, f, HIGHEST_PROTOCOL)

    def add_binding(self, local_folder, remote_folder, repository_url=None,
                    username=None, password=None):
        self.reload_bindings()
        local_folder = os.path.abspath(local_folder)
        b = self.get_binding(local_folder)
        if b is not None:
            raise ValueError("Cannot bind '%s' since '%s' is already bound to"
                             " '%s/%s'" % (local_folder, b.local_folder,
                                           b.repository_url, b.remote_folder))

        binding = Binding(local_folder, remote_folder, repository_url,
                          username, password)
        self.bindings.append(binding)
        self.persist_bindings()
        return binding

    def list_bindings(self):
        self.reload_bindings()
        return self.bindings[:]

    def get_binding(self, local_path):
        self.reload_bindings()
        local_path = os.path.abspath(local_path)
        for binding in self.bindings:
            if local_path.startswith(binding.local_folder):
                return binding
        return None

    def get_state(self, binding, path):
        self.reload_states()
        return self.states.get((binding, path), CompoundState(binding, path))

    def set_state(self, binding, state):
        self.reload_states()
        self.states[(binding, state.path)] = state
        self.persist_states()

    def get_states(self, binding):
        self.reload_states()
        return dict((p, s) for (b, p), s in self.states.iteritems()
                    if b == binding)

    def delete_state(self, binding, path):
        self.reload_states()
        del self.states[(binding, path)]
        for (b, p), s in self.states.items():
            if b == binding and p.startswith(path + '/'):
                del self.states[(binding, p)]

        # also delete all subpath
        self.persist_states()

