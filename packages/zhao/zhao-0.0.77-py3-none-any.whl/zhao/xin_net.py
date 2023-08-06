#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""提供网络操作相关的实现
"""

__author__ = 'Zhao Xin <7176466@qq.com>'
__copyright__ = 'All Rights Reserved © 1975-2018 Zhao Xin'
__license__ = 'GNU General Public License v3 (GPLv3)'
__version__ = '2018-03-28'

import urllib.request
import json
from zhao.xin_re import regex_pattern, REGEX_IPV4

PATTERN_IPV4 = regex_pattern(REGEX_IPV4)


def get_public_ip():
    try:
        response = urllib.request.urlopen('http://httpbin.org/ip')
        data = json.loads(response.read().decode()).get('origin', '')
        return PATTERN_IPV4.fullmatch(data).group()
    except (IOError, AttributeError, json.decoder.JSONDecodeError, KeyError, IndexError):
        return ''


if __name__ == '__main__':
    print(get_public_ip())
