#!/usr/bin/env python3

def _do_with(fname, mode, cmd, *args, **kwargs):
    with open(fname, mode) as f:
        return getattr(f, cmd)(*args, **kwargs)

def read(fname):
    return _do_with(fname, 'r', 'read')

def readline(fname):
    return _do_with(fname, 'r', 'readlines')

def readlines(fname):
    return _do_with(fname, 'r', 'readlines')

def readb(fname):
    return _do_with(fname, 'rb', 'read')

def write(fname, contents):
    return _do_with(fname, 'w', 'write', contents)

def writeb(fname, contents):
    return _do_with(fname, 'wb', 'write', contents)
