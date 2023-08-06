#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""本模块提供网络操作相关的实现
"""

__author__ = 'Zhao Xin <7176466@qq.com>'
__copyright__ = 'All Rights Reserved © 1975-2018 Zhao Xin'
__license__ = 'GNU General Public License v3 (GPLv3)'
__version__ = '2018-03-28'
__all__ = ['local_mac_addr', 'local_public_ip', 'ip_info', 'ping']

import urllib.request
import urllib.parse
import subprocess
import json
import uuid
import requests
from zhao.xin_re import regex_pattern, REGEX_IPV4
from zhao.xin_os import IS_WINDOWS

PATTERN_IPV4 = regex_pattern(REGEX_IPV4)


def local_mac_addr()->str:
    """返回本地默认网卡MAC地址
    """
    mac = uuid.getnode()
    return ':'.join('%02X' % (mac >> i & 0xff) for i in (40, 32, 24, 16, 8, 0))


def local_public_ip()->str:
    """返回本地公网IP地址
    """
    ipv4 = ''
    try:
        response = urllib.request.urlopen('http://httpbin.org/ip')
        data = json.loads(response.read().decode()).get('origin', '')
        ipv4 = PATTERN_IPV4.fullmatch(data).group()
        if not ipv4:
            ipv4 = PATTERN_IPV4.fullmatch(ip_info()['ip']).group()
    except (IOError, AttributeError, json.decoder.JSONDecodeError, KeyError, IndexError):
        pass
    return ipv4


def ip_info(ipv4='')->dict:
    """查询IP地址的详细信息
    ipv4 默认为空，即表示查询本地公网IP的信息
    """
    result = {
        'ip': '',
        'country_name': '',
        'country': '',
        'region': '',
        'region_code': '',
        'city': '',
        'latitude': 0.0,
        'longitude': 0.0,
        'timezone': '',
        'continent_code': '',
        'utc_offset': '',
        'country_calling_code': '',
        'languages': '',
        'currency': '',
        'asn': '',
        'org': '',
        'postal': None,
        'error': False,
        'reason': '',
    }
    try:
        api_url = urllib.parse.urljoin('https://ipapi.co', '%s/json' % ipv4)
        content = urllib.request.urlopen(api_url).read().decode('utf-8')
        result.update(json.loads(content))
    except (urllib.error.URLError, urllib.error.HTTPError):
        pass
    return result


def ping(host):
    """返回与host是否连通
    """
    success = False
    try:
        success = subprocess.call(['ping', '-n1' if IS_WINDOWS else '-c1', '-w2', '-W2', host],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3.0) == 0
    except subprocess.TimeoutExpired:
        pass
    return success


def is_online():
    """检查外网连通是否正常
    """
    return any((requests.head(url, timeout=3.0).status_code == 200 for url in ('http://www.163.com',
                                                                               'http://www.baidu.com',
                                                                               'http://www.sina.com.cn')))


if __name__ == '__main__':
    print(local_mac_addr())
    print(local_public_ip())
    print(ip_info())
    print('ping www.baidu.com', ping('www.baidu.com'))
    print('ping www.google.com', ping('www.google.com'))
