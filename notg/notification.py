"""Platform neutral notification.

"""

# Cut and pasted from PyZen 0.1
# Should be Copyright: 'Noah Kantrowitz' and licensed under the BSD license.

import subprocess
import sys

try:
    import pynotify
except ImportError:
    pynotify = None


class AppleScriptError(Exception):
    pass


class Notifier(object):
    def notify(self, type, title, msg):
        raise NotImplementedError


class GrowlNotifier(Notifier):

    def __init__(self):
        self.has_growl = self.is_growl_running()
        if self.has_growl:
            self.register_app()

    def is_growl_running(self):
        """Check if Growl is running. Run this before any other Growl functions."""
        script = """
        tell application "System Events"
            return count of (every process whose name is "GrowlHelperApp") > 0
        end tell
        """
        return self.run_script(script)

    def register_app(self):
        script= """
        tell application "GrowlHelperApp"
         -- Make a list of all the notification types
         -- that this script will ever send:
         set the notificationsList to {"Test Successful" , "Test Failure"}

         -- Register our script with growl.
         -- You can optionally (as here) set a default icon
         -- for this script's notifications.
         register as application "ZenTest" all notifications notificationsList default notifications notificationsList
        end tell"""
        self.run_script(script)

    def notify(self, type, title, msg):
        if self.has_growl:
            script= """
            tell application "GrowlHelperApp"
              notify with name "%s" title "%s" description "%s" application name "ZenTest"
            end tell""" % (type, title, msg)
            self.run_script(script)

    def run_script(self, script):
        proc = subprocess.Popen(['osascript', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate(script)
        if proc.returncode:
            raise AppleScriptError('osascript failure: %s'%err)
        out = out.strip()
        if out == 'true':
            return True
        elif out == 'false':
            return False
        elif out.isdigit():
            return int(out)
        else:
            return out


class LibnotifyNotifier(Notifier):

    def notify(self, type, title, msg):
        if pynotify:
            n = pynotify.Notification(title, msg)
            n.show()


class Win32Notifier(object):
    def __init__(self):
        from win32.wrappers import SystrayIconThread
        self.thread = SystrayIconThread()
        self.thread.start()

    def notify(self, type, title, msg, icon=""):
        self.thread.notify(title, msg, icon+'.ico')

    def shutdown(self):
        self.thread.quit()
        self.thread.join()


class NullNotifier(object):
    def notify(self, type, title, msg):
        pass


if sys.platform == "darwin":
    notifier = GrowlNotifier()
elif sys.platform == "linux":
    notifier = LibnotifyNotifier()
elif sys.platform == "win32":
    notifier = Win32Notifier()
else:
    notifier = NullNotifier()


def notify(type, title, msg):
    notifier.notify(type, title, msg)