# Nuxeo On the Go

Synchronizes a local folder with a remote Nuxeo server.

Currently uses the CMIS protocol, though more efficient protocols may be
investigated.


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


## About Nuxeo

Nuxeo provides a modular, extensible Java-based [open source software platform
for enterprise content management](http://www.nuxeo.com/en/products/ep) and
packaged applications for [document
management](http://www.nuxeo.com/en/products/document-management), [digital
asset management](http://www.nuxeo.com/en/products/dam) and [case
management](http://www.nuxeo.com/en/products/case-management). Designed by
developers for developers, the Nuxeo platform offers a modern architecture, a
powerful plug-in model and extensive packaging capabilities for building
content applications.

More information on: <http://www.nuxeo.com/>
