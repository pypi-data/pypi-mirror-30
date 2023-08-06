#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Common Module
"""
import os
import time
import errno
from contextlib import contextmanager


def md5(data):
    """Return MD5 hash string of the data
    """
    if not isinstance(data, bytes):
        data = str(data).encode('utf-8')
    import hashlib
    return hashlib.md5(data).hexdigest()


def create_cipher(key):
    """create a cipher to encrypt and decrypt"""
    from base64 import urlsafe_b64encode
    from cryptography.fernet import Fernet
    key = urlsafe_b64encode(md5(key).encode('utf-8'))
    cipher = Fernet(key)
    return cipher


def strftime2(old, string, new_fmt=r'%Y-%m-%d', default='1970-01-01'):
    """convert time from format to another format"""
    try:
        return time.strftime(new_fmt, time.strptime(string, old))
    except ValueError:
        return default


def check_path(path):
    """return True if the path exists or success create of it"""
    return (os.path.isdir(path) or (not os.path.isfile(path)
                                    and os.makedirs(path)
                                    or os.path.isdir(path)))


def is_readable_file(path):
    """Return True if it is a file and it is readable"""
    return os.path.isfile(path) and os.access(path, os.R_OK)


@contextmanager
def open_file(path, filename, mode='r', overwrite=False, ignore_error=False):
    """open function for human
    """
    # path can be a list of subpath to be joined together
    if isinstance(path, list):
        path = os.path.join(path)

    target = os.path.join(path, filename)  # fullpath to read/write

    if mode.startswith('r'):
        if not is_readable_file(target) and ignore_error:
            target = '/dev/null'  # ignore error and read '' from null
    # prevent to overwrite existing file
    elif os.path.isfile(target):
        if not overwrite:
            if ignore_error:
                target = '/dev/null'  # ignore error and write at will
            else:
                raise OSError(errno.EEXIST,
                              'try to overwrite an existing file: %r' % target)
    # create the path to write the target file
    elif not os.path.exists(path):
        os.makedirs(path)

    # do open ... yield ... close ...
    the_file = open(target, mode)
    yield the_file
    the_file.close()
