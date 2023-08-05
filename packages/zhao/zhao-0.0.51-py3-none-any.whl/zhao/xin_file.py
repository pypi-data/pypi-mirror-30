# -*- coding: utf-8 -*-
"""This module provides file related classes and functions.
"""

from os import rename
from shutil import copy2 as copy, move, copytree
from hashlib import md5


def binread(path, chunk=1048576):
    with open(path, 'rb') as datafile:
        data = datafile.read(chunk)
        while data:
            yield data
            data = datafile.read(chunk)


def md5file(path, chunk=1048576, hexdigest=True):
    md5hash = md5()
    for data in binread(path, chunk):
        md5hash.update(data)
    return md5hash.hexdigest() if hexdigest else md5hash.digest()
