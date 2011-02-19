#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "nuxeo-otg",
    description = 'Nuxeo On the Go - Synchronize folders with a Nuxeo repo',
    version = '0.1.0',
    author = 'Nuxeo',
    author_email = 'nuxeo-dev@lists.nuxeo.org',
    license = 'LGPL',
    url = 'http://github.com/nuxeo/nuxeo-otg/',
    # TODO: rewrite the README.md as README.rst to reuse it for the pypi page
    # long_description = open('README.rst', 'rb').read(),
    packages = ['notg'],
    scripts = ['scripts/notg'],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
