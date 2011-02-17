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

Nuxeo provides a modular, extensible Java-based [open source software platform for enterprise content management] [1] and packaged applications for [document management] [2], [digital asset management] [3] and [case management] [4]. Designed by developers for developers, the Nuxeo platform offers a modern architecture, a powerful plug-in model and extensive packaging capabilities for building content applications. 

[1]: http://www.nuxeo.com/en/products/ep
[2]: http://www.nuxeo.com/en/products/document-management
[3]: http://www.nuxeo.com/en/products/dam
[4]: http://www.nuxeo.com/en/products/case-management

More information on: <http://www.nuxeo.com/>
