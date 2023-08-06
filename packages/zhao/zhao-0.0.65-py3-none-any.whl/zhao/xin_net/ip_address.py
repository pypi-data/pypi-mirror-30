# -*- coding: utf-8 -*-
"""zhao.xin_net.ip_address
"""

import requests


def ip_needle(_ip=''):
    """IP探针

    参数:
        _ip 字符串，为空时查询本地公共ip

    返回:
        json 数据，如:
        {
            'ip': '114.222.99.82',
            'city': 'Nanjing',
            'region': 'Jiangsu',
            'region_code': '32',
            'country': 'CN',
            'country_name': 'China',
            'postal': None,
            'latitude': 32.0617,
            'longitude': 118.7778,
            'timezone': 'Asia/Shanghai',
            'asn': 'AS4134',
            'org': 'No.31,Jin-rong Street'
        }
    """
    return requests.get(f'https://ipapi.co/{_ip}/json').json()


if __name__ == '__main__':
    print(f'IP address: {ip_needle()}')
