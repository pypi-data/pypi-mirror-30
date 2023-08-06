#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""zhao.xin_net module
"""

__version__ = '2018-03-23'
__license__ = 'GPLv3'
__author__ = 'Zhao Xin <7176466@qq.com>'
__copyright__ = 'All rights reserved © 1975-2018 Zhao Xin'

import urllib.request
import json
import re

IPV4_ADDR_REP = re.compile(r'((?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)){3})')


def query_public_ip():
    try:
        response = urllib.request.urlopen('http://httpbin.org/ip')
        content = response.read()
        text = content.decode()
        data = json.loads(text)
        match = IPV4_ADDR_REP.fullmatch(data['origin'])
        return match.group(1)
    except (IOError, json.decoder.JSONDecodeError, KeyError, IndexError, AttributeError):
        pass
