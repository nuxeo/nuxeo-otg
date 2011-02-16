
class Client(object):
    """Client for a specific API."""

    def __init__(self, root, username, password):
        self.root = root
        self.username = username
        self.password = password

    def get_tree(self):
        pass