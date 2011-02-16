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


