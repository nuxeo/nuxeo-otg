# Nuxeo On the Go

Synchronizes a local folder with a remote Nuxeo server.

Currently uses the CMIS protocol, though more efficient protocols may be
investigated.


## Current state

This code is very very alpha quality (result of 2 days sprint at
Nuxeo). It will probably eat your data in it's current state.


## Building

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

To test, type:

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
