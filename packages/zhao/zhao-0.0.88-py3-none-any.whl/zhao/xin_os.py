#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本模块提供操作系统操作相关的实现
"""
__author__ = 'Zhao Xin <7176466@qq.com>'
__copyright__ = 'All Rights Reserved © 1975-2018 Zhao Xin'
__license__ = 'GNU General Public License v3 (GPLv3)'
__version__ = '2018-03-28'

import os
import sys
import platform

IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

HOME_PATH = os.path.expanduser('~')                                 # 用户家路径
BASE_PATH = os.path.abspath(os.path.curdir)                         # 当前路径
try:
    MAIN_PATH = os.path.dirname(sys.modules['__main__'].__file__)   # 主模块所在路径
except (IndexError, AttributeError):
    MAIN_PATH = BASE_PATH


def path_join(path, *subs):
    return os.path.join(str(path), *map(str, subs))


def path_is_writable(path, *subs):
    "Try to makedirs the full-path and return if it is now a writable dir"
    try:
        _path = path_join(path, *subs)
        os.path.exists(_path) or os.makedirs(_path)
        return os.path.isdir(_path) and os.access(_path, os.W_OK | os.X_OK)
    except os.error:
        return False


def write_file(data, path, *subs):
    "Return True if the data has been written successfully"
    _path = path_join(path, *subs)
    if path_is_writable(os.path.dirname(_path)) is True:
        _mode = 'wb' if isinstance(data, bytes) else 'w'
        try:
            with open(_path, _mode) as _file:
                return _file.write(data) == len(data)
        except os.error:
            pass
    return False
