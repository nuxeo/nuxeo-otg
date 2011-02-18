#!/usr/bin/env python

from optparse import OptionParser
import logging
import sys
from notg.controller import Controller

# hardcoded parameters while storage is not persistent
LOCAL_FOLDER='C:\\notg-test'
REMOTE_FOLDER='/default-domain/workspaces'
REPOSITORY_URL='http://localhost:8080/nuxeo/atom/cmis'
USERNAME='Administrator'
PASSWORD='Administrator'

parser = OptionParser()
parser.add_option("-v", "--verbose", dest="verbose", action='store_true',
                  default=False, help="Log synchronisation info to stdout")

(options, args) = parser.parse_args()

if options.verbose:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s')

if len(args) < 1:
    print "ERROR: need a command as first argument: status, regresh or sync"
    sys.exit(1)

cmd = args[0]
local_folder = args[1] if len(args) == 2 else None

ctl = Controller()

# hardcoded binding for noew
ctl.attach(LOCAL_FOLDER, REMOTE_FOLDER, repository_url=REPOSITORY_URL,
           username=USERNAME, password=PASSWORD)

if cmd == 'status':
    print ctl.status(local_folder)
elif cmd == 'refresh':
    ctl.refresh(local_folder=local_folder, async=False)
elif cmd == 'sync':
    ctl.synchronize(local_folder=local_folder, async=False)
else:
    print "ERROR: unknown command: " + cmd
    sys.exit(1)

