#!/usr/bin/env python3

import os
from distutils.core import setup as _setup

def _trim_layers(path, num=0):
    if num <= 0:
        return path
    pieces = path.split(os.sep)
    if len(pieces) <= num:
        return ''
    else:
        return os.path.join(*pieces[num:])

def _find_packages(parent='src'):
    trim_depth = len([p for p in parent.split(os.sep) if p])
    packages = {}
    for root, dirs, files in os.walk(parent):
        for fname in dirs:
            fpath = os.path.join(root, fname)
            tpath = _trim_layers(fpath,trim_depth)
            packages[tpath] = fpath
    return packages

def setup(**kwargs):
    if 'requires' not in kwargs:
        requirements_txt = os.path.join(os.getcwd(), "requirements.txt")
        if os.path.exists(requirements_txt):
            with open(requirements_txt) as f:
                lines = f.readlines()
                kwargs['requires'] = [l.strip() for l in lines if l.strip()]


    if 'packages' not in kwargs and 'package_dir' not in kwargs and 'source_dir' in kwargs:
        # kwargs['package_dir'] = {'':kwargs['source_dir']}
        kwargs['package_dir'] = _find_packages(kwargs['source_dir'])
        del kwargs['source_dir']
        kwargs['packages'] = list(kwargs['package_dir'].keys())
    if 'scripts' not in kwargs and 'script_dir' in kwargs:
        scripts = [os.path.join(kwargs['script_dir'], f) for f in os.listdir(kwargs['script_dir']) if not '~' in f and not '#' in f]
        del kwargs['script_dir']
        if scripts:
            kwargs['scripts'] = scripts
    return _setup(**kwargs)
