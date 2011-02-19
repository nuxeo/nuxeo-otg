# Nuxeo On the Go

Synchronizes a local folder with a remote Nuxeo server.

Currently uses the CMIS protocol, though more efficient protocols may be
investigated.


## Current state

WARNING: This code is very very alpha quality (result of 2 days sprint
at Nuxeo). It will *eat your data*, especially in case of concurrent
editing situations.


## Installing system wide

Install the dependencies, e.g. under Linux and OSX:

    sudo pip install -r dependencies.txt

Then install notg itself:

    sudo python setup.py install


## Usage

Create a workspace in Nuxeo and a new local folder on your desktop

Then tell notg to bind them with:

    notg attach --local-folder notg_workspace \
                --remote-folder /default-domain/workspaces/Workspace \
                --repository-url http://localhost:8080/nuxeo/atom/cmis \
                --username Administrator --password Administrator

    touch /home/ogrisel/notg_workspace/empty_file.txt

You can then ask notg to scan their content and then list the status of the
files with:

    notg refresh

    notg status
    /home/ogrisel/notg_workspace/empty_file.txt    locally_created

You can then manually trigger a sync with:

    notg sync
    2011-02-19 19:23:34,668 INFO Pushing new object with path: empty_file.txt

    notg status
    /home/ogrisel/notg_workspace/empty_file.txt    synchronized

To automatically scan both the server and the local folder and sync their
content use:

    notg autosync

Use Ctrl-C to interrupt. A real daemon mode is planned.

To unlink the folders and reset all meta-data tracked by Nuxeo On the Go,
simply delete the `~/.nuxeo-otg` folder.


## Building locally (for developers)

First, you need to make sure you have:

- python 2.6 or 2.7
- virtualenv and pip

To install the needed dependencies, type:

    make env

On linux you might need to install libyaml-dev first:

    sudo apt-get install libyaml-dev
    make env

Then type:

    . env/bin/activate


## Testing

Install a Nuxeo DM 5.4.0+ instance from http://nuxeo.com and launch it (default
settings are fine for testing).

Then in the `nuxeo-otg` folder type:

    make test


## Roadmap, TODOs, shortcomings

- implement asynchronous process that continuously refresh & synchronize using polling
- use watchdog to monitor FS incrementally instead of local polling
- use smart CMISQL queries to only download the properties for files that have
  changed (need access to the audit log to detect deleted files)
- use digest to ensure that files have really changed or don't need a sync
- implement local client renaming of files in conflicted state
- implement a better storage for metadata (currently load everything in memory
  an greedily hit the disk with the pickle module): use sqlite / SQLAlchemy
  instead


## About Nuxeo

Nuxeo provides a modular, extensible Java-based [open source software platform for enterprise content management] [1] and packaged applications for [document management] [2], [digital asset management] [3] and [case management] [4]. Designed by developers for developers, the Nuxeo platform offers a modern architecture, a powerful plug-in model and extensive packaging capabilities for building content applications.

[1]: http://www.nuxeo.com/en/products/ep
[2]: http://www.nuxeo.com/en/products/document-management
[3]: http://www.nuxeo.com/en/products/dam
[4]: http://www.nuxeo.com/en/products/case-management

More information on: <http://www.nuxeo.com/>
