# -*- coding: utf-8 -*-
"""zhao.xin_net.ping
"""

from platform import system
import subprocess

_N_C = '-n' if system() == 'Windows' else '-c'


def is_host_active(host):
    """check if host is active and return True/False"""
    error = subprocess.call(['ping', _N_C, '1', '-w', '1', '-W', '1', host],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return error == 0


if __name__ == '__main__':
    print(is_host_active('www.baidu.com'))
    print(is_host_active('www.163.com'))
    print(is_host_active('www.google.com'))
