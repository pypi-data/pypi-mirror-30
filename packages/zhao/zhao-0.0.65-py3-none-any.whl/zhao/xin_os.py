# -*- coding: utf-8 -*-
"""zhao.xin_os
This module extends the os module of the standard libary.
"""

import os
import sys
import errno

USER_HOME_PATH = os.path.expanduser('~')
CURRENT_WORKING_PATH = os.path.abspath(os.path.curdir)
try:
    MAIN_PATH = os.path.abspath(
        os.path.dirname(sys.modules['__main__'].__file__))
except (IndexError, AttributeError):
    MAIN_PATH = CURRENT_WORKING_PATH


def is_readable(path):
    """判断路径是否可读"""
    return os.access(path, os.R_OK)


def is_writeable(path):
    """判断路径是否可写"""
    return os.access(path, os.W_OK)


def mkdirs(path, mode=0o755):
    """递归地创建多级路径
    """
    head, tail = os.path.split(path)
    if not tail:
        head, tail = os.path.split(head)
    if tail:
        try:
            mkdirs(head, mode)
            os.mkdir(path, mode)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise error


def readable_size(size, binary=True, string=True):
    """将数据大小转换为人类友好的格式
    """
    assert size >= 0, 'size should be positive!'
    multiple = 1024.0 if binary else 1000.0
    units = {
        1000: ['YB', 'ZB', 'EB', 'PB', 'TB', 'GB', 'MB', 'KB'],
        1024: ['YiB', 'ZiB', 'EiB', 'PiB', 'TiB', 'GiB', 'MiB', 'KiB']
    }.get(multiple, [])
    unit = 'B'
    while size >= multiple and units:
        size /= multiple
        unit = units.pop()
    return f'{size:0.2f} {unit}' if string else (size, unit)


def all_dirs_in(path):
    """路径下所有的子路径
    """
    for curdir, dirnames, _ in os.walk(os.path.abspath(path)):
        for subdir in dirnames:
            yield os.path.join(curdir, subdir)


def all_files_in(path):
    """路径下所有的文件
    """
    for curdir, _, filenames in os.walk(os.path.abspath(path)):
        for filename in filenames:
            yield os.path.join(curdir, filename)


def files_size(*filenames):
    """计算多个文件的总大小
    """
    filenames = set(filenames)  # 去重
    return sum(map(os.path.getsize, filenames))


def block_size(path):
    """磁盘簇大小
    """
    return os.statvfs(path).f_bsize
