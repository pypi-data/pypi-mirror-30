#!/usr/bin/env python3

import io
import os
import tempfile
import zipfile

from calvin.shell import execute

def strip_prepath(path, prepath):
    if path.startswith(prepath):
        path = path[len(prepath):]
    if path and path[0] == "/":
        path = path[1:]
    return path

def add_directory_to_zipfile(zipf, directory):
    for root, dirs, files in os.walk(directory):
        arcpath = strip_prepath(root, directory)
        for file in files:
            if file[-1] != "~":
                fname = os.path.join(root, file)
                arcname = os.path.join(arcpath, file)
                zipf.write(fname, arcname)

def create_zipfile(directory):
    zflo = io.BytesIO()
    zipf = zipfile.ZipFile(zflo, 'w', zipfile.ZIP_DEFLATED)
    add_directory_to_zipfile(zipf, directory)
    requirements_txt_path = os.path.join(directory, 'requirements.txt')
    if not os.path.isfile(requirements_txt_path):
        pass
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            code, out, err = shell.execute('pip install -r {requirements} -t {tempdir}'.format(requirements=requirements_txt_path, tempdir=tempdir))
            add_directory_to_zipfile(zipf, tempdir)
        pass
    zipf.close()
    body = io.BytesIO(zflo.getvalue()).read()
    return body
