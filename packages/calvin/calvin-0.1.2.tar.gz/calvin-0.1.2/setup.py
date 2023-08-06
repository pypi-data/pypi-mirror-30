#!/usr/bin/env python3

from distutils.core import setup

MAJOR_VERSION='0'
MINOR_VERSION='1'
PATCH_VERSION='2'

VERSION = "{}.{}.{}".format(MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION)

setup(
    name = 'calvin',
    packages = ['calvin','calvin/aws'],
    version = VERSION,
    description = 'Random python utilities.',
    author = 'Steve Norum',
    author_email = 'sn@littlestviking.com',
    url = 'https://github.com/stevenorum/calvin',
    download_url = 'https://github.com/stevenorum/calvin/archive/{}.tar.gz'.format(VERSION),
    keywords = ['utils','aws','lambda','cli'],
    classifiers = [],
)
