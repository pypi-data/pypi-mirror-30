#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""本模块提供网络操作相关的实现
"""

__author__ = 'Zhao Xin <7176466@qq.com>'
__copyright__ = 'All Rights Reserved © 1975-2018 Zhao Xin'
__license__ = 'GNU General Public License v3 (GPLv3)'
__version__ = '2018-03-28'

import urllib.request
import json
from zhao.xin_re import PATTERN_IPV4


# def get_public_ip():
#     try:
#         response = urllib.request.urlopen('http://httpbin.org/ip', timeout=(3.0, 5.0))
#         content = response.read()
#         data = json.loads(content.decode()).get('origin', '')
#         print(PATTERN_IPV4.fullmatch(data))
#         return match.group(1)
#     except (IOError, AttributeError, json.decoder.JSONDecodeError, KeyError, IndexError):
#         return ''


# print(get_public_ip())
