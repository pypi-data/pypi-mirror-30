#!/usr/bin/env python3

import shlex
import subprocess

def execute(cmd, raise_on_error=True):
    resp = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    code = resp.returncode
    out = resp.stdout.decode('utf-8')
    err = resp.stderr.decode('utf-8')
    if raise_on_error and code != 0:
        raise RuntimeError('Command failed: {}\nExit code: {}:\nstderr: {}\nstdout: {}'.format(cmd, code, err, out))
    return code, out, err
