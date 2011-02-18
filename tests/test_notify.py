import unittest

from notg import notification

class NotifyTest(unittest.TestCase):

    def test(self):
        notification.notify("Test", "Title", "Message")