#!/usr/bin/env python

from optparse import OptionParser
import logging
import sys
from notg.controller import Controller
from os.path import join

commands = (
    'attach',
    'status',
    'refresh',
    'sync',
)


def setup_logs(options):
    if options.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(message)s')


def handle_attach(args, parser):
    parser.add_option("-l", "--local-folder", dest="local_folder",
                      help="Path of the local folder to synchronize")
    parser.add_option("-r", "--remote-folder", dest="remote_folder",
                      help=("Path of the remote folder to synchronize"
                            " from the root of the repository."))
    parser.add_option("-L", "--repository-url", dest="repository_url",
                      help="URL of the CMIS endpoint")
    parser.add_option("-u", "--username", dest="username",
                      help="Username for CMIS access to the remote folder")
    parser.add_option("-p", "--password", dest="password",
                      help="Password for CMIS access to the remote folder")
    options, args = parser.parse_args(args)
    setup_logs(options)

    if not options.local_folder or not options.local_folder:
        print "ERROR: both --local-folder and --remote-folder are required"
        parser.print_help()
        sys.exit(3)

    ctl = Controller()
    ctl.attach(options.local_folder, options.remote_folder,
               repository_url=options.repository_url,
               username=options.username,
               password=options.password)


def handle_status(args, parser):
    options, args = parser.parse_args(args)
    setup_logs(options)
    status_list = Controller().status(args)
    for binding_folder, path, state in status_list:
        print "%s\t%s" % (join(binding_folder, path), state)


def handle_refresh(args, parser):
    parser.add_option("-a", "--async", dest="async", action='store_true',
                      default=False, help="Perform operation asynchronously.")
    options, args = parser.parse_args(args)
    setup_logs(options)
    Controller().refresh(args, async=options.async)


def handle_sync(args, parser):
    parser.add_option("-a", "--async", dest="async", action='store_true',
                      default=False, help="Perform operation asynchronously.")
    options, args = parser.parse_args(args)
    setup_logs(options)
    Controller().synchronize(args, async=options.async)


if __name__ == '__main__':
    # common options
    usage = "usage: %prog cmd [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-v", "--verbose", dest="verbose", action='store_true',
                      default=False, help="log synchronisation info to stdout")

    args = sys.argv
    if len(args) < 2:
        print "ERROR: need a command as first argument:"
        print ", ".join(commands)
        sys.exit(1)

    cmd = args[1]
    args = args[2:]
    if cmd not in commands:
        print "ERROR: %s is not a valid command, try:" % cmd
        print ", ".join(commands)
        sys.exit(2)

    try:
        locals()['handle_' + cmd](args, parser)
    except Exception as e:
        logging.error(e)

