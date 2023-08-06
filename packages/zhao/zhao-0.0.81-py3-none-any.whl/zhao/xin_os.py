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
