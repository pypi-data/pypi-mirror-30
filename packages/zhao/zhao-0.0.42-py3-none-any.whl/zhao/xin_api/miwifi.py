# -*- coding:utf-8 -*-
"""小米路由器API
"""

import re
import random
from hashlib import sha1
import time
import requests


class MiWiFi(object):
    """小米路由器API

    使用方法：
        MIWIFI = MiWiFi(password='小米路由器WEB登录密码')
        if MIWIFI.is_offline:
            if MIWIFI.reconnect():
                printf('自动重新拨号成功')
            else:
                printf('自动重新拨号失败')
    """

    def __init__(self, password):
        self.session = requests.Session()
        self.password = password.encode()
        self.token = self._token

    @property
    def is_online(self):
        """外网联通正常
        """
        for url in ('http://www.163.com',
                    'http://www.baidu.com',
                    'http://www.sina.com.cn'):
            if requests.head(url).status_code == 200:
                return True
        return False

    @property
    def is_offline(self):
        """外网已经掉线
        """
        return not self.is_online

    @property
    def _token(self):
        """小米路由器访问令牌
        """
        try:
            # get nonce
            response = self.session.get('http://miwifi.com/cgi-bin/luci/web')
            key = re.findall(r"key:\s*'(.*?)'", response.text)[0].encode()
            mac = re.findall(r"deviceId = '(.*)'", response.text)[0].encode()
            nonce = f'0_{mac}_{time.time():.0f}_{random.random() * 10000:04.0f}'
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
        url = f'http://miwifi.com/cgi-bin/luci/;stok={self.token}/api/xqnetwork/{action}'
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
            url = f'http://miwifi.com/cgi-bin/luci/;stok={self.token}/api/xqsystem/device_list'
            return self.session.get(url).json()['list']
        except Exception:
            return []

    def __del__(self):
        self.session.close()
