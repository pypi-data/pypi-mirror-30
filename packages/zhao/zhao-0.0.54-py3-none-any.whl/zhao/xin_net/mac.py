# -*- coding: utf-8 -*-
"""zhao.xin_net.mac
"""

import uuid


def get_mac():
    """获取默认网卡的MAC号
    """
    mac = uuid.getnode()
    return ':'.join(f'{mac>>i&0xff:02x}' for i in (40, 32, 24, 16, 8, 0))


if __name__ == '__main__':
    print(f'MAC address: {get_mac()}')
