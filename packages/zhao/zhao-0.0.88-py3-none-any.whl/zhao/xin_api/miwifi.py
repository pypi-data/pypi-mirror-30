#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""小米路由器API类
"""

__author__ = 'Zhao Xin <7176466@qq.com>'
__copyright__ = 'All rights reserved © 1975-2018 Zhao Xin'
__license__ = 'GNU General Public License v3 (GPLv3)'
__version__ = '2018-03-28'

import os
import re
import time
import random
from hashlib import sha1
import requests
from zhao.xin_net import is_online


class MiWiFi(object):
    """小米路由器API类

    使用方法：
        MIWIFI = MiWiFi(password='小米路由器WEB登录密码')
        if MIWIFI.is_offline:
            if MIWIFI.reconnect():
                printf('自动重新拨号成功')
            else:
                printf('自动重新拨号失败')
    """

    def __init__(self, password=os.environ.get('MIWIFI_PASSWORD')):
        self.session = requests.Session()
        self.password = password.encode()
        self.token = self._token

    def __del__(self):
        self.session.close()

    @property
    def is_online(self):
        """外网联通正常
        """
        return is_online()

    @property
    def is_offline(self):
        """外网已经掉线
        """
        return not is_online()

    @property
    def _token(self):
        """小米路由器访问令牌
        """
        try:
            # get nonce
            response = self.session.get('http://miwifi.com/cgi-bin/luci/web')
            key = re.findall(r"key:\s*'(.*?)'", response.text)[0].encode()
            mac = re.findall(r"deviceId = '(.*)'", response.text)[0].encode()
            nonce = '0_{}_{:.0f}_{:04.0f}'.format(mac, time.time(), random.random() * 10000)
            # hash the password
            password = sha1(
                (nonce + sha1(self.password + key).hexdigest()).encode()).hexdigest()
            # prepare the payload for getting the token
            payload = {'username': 'admin',
                       'logtype': '2',
                       'nonce': nonce,
                       'password': password}
            token = self.session.post('http://miwifi.com/cgi-bin/luci/api/xqsystem/login',
                                      data=payload).json()['token']
            return token
        except Exception:
            return ''

    def _do(self, action):
        url = 'http://miwifi.com/cgi-bin/luci/;stok={}/api/xqnetwork/{}'.format(self.token, action)
        return self.session.get(url).json()

    def disconnect(self):
        """断开 ADSL
        """
        try:
            return self._do('pppoe_stop')['code'] == 0
        except Exception:
            return False

    def connect(self):
        """连接 ADSL
        """
        try:
            return self._do('pppoe_start')['code'] == 0
        except Exception:
            return False

    def reconnect(self):
        """重新连接 ADSL
        """
        if self.disconnect():
            time.sleep(10)
            if self.connect():
                time.sleep(20)
        return self.is_online

    @property
    def public_ip(self):
        """外网IP
        """
        try:
            return self._do('pppoe_status')['ip']['address']
        except Exception:
            return ''

    @property
    def device_list(self):
        """已连接的设备列表
        """
        try:
            url = 'http://miwifi.com/cgi-bin/luci/;stok={}/api/xqsystem/device_list'.format(self.token)
            return self.session.get(url).json()['list']
        except Exception:
            return []


if __name__ == '__main__':
    MIWIFI = MiWiFi()
    print('在线' if MIWIFI.is_online else '掉线')
    print(MIWIFI.public_ip)
    print(MIWIFI.device_list)
