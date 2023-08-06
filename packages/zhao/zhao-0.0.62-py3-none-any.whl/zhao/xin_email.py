#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""zhao.xin_email 模块提供电子邮件相关的实现
"""

import re
import atexit
import socket
import smtplib
import email.utils
from email.message import EmailMessage

__all__ = ['Mailman']

_EMAIL_ADDR_REGEX_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I | re.S | re.X)


def _all_email_addresses_from(obj):
    return (match.group() for match in _EMAIL_ADDR_REGEX_PATTERN.finditer(str(obj)))


class Mailman:
    """电子邮件类 Mailman(host, user, password, tls=True)

    实例化: Mailman(host, user, password)
    属性: bool ready，标志与SMTP服务器连接、登录状态均正常。
    方法: bool send(sender, receivers, subject, content)，用于发送邮件，返回True表示发送成功。

    注: 暂时仅支持不带附件的纯文本邮件。
    """

    def __init__(self, host, user, password, tls=True):
        self._host = host
        self._user = user
        self._password = password
        self._tls = tls
        self._server = None
        self._connect()
        atexit.register(self._disconnect)

    def __str__(self):
        return 'Mailman: Host=%r, User=%r, Password=%r, TLS=%r, Ready=%r' % (self._host, self._user,
                                                                             '******' if bool(self._password) else None,
                                                                             self._tls, self.ready)

    def _disconnect(self):
        try:
            self._server.quit()
        except (socket.gaierror, smtplib.SMTPException, AttributeError):
            pass

    def _connect(self)->bool:
        try:
            self._server = smtplib.SMTP(host=self._host)
            self._server.ehlo()
            if self._tls:
                assert self._server.starttls()[0] == 220, 'failed to start TLS mode .'
            assert self._server.login(user=self._user, password=self._password)[0] == 235, 'smtp server login error.'
            return self._connected
        except (socket.gaierror, smtplib.SMTPException, AttributeError, IndexError, AssertionError):
            return False

    @property
    def _connected(self)->bool:
        try:
            assert self._server and self._server.noop() == (250, b'Ok'), 'noop got no response.'
            return True
        except (socket.gaierror, smtplib.SMTPException, AttributeError, AssertionError):
            return False

    @property
    def ready(self)->bool:
        return self._connected or self._connect()

    def send(self, sender: str, receivers, subject: str, content: str)->bool:
        success = False
        if self.ready:
            mail = EmailMessage()
            mail['From'] = sender
            mail['To'] = ', '.join(_all_email_addresses_from(str(receivers)))
            mail['Date'] = email.utils.formatdate(localtime=True)
            mail['Subject'] = subject
            mail.set_content(content)
            success = self._server.send_message(mail) == {}
        return success


if __name__ == '__main__':
    # 测试发送
    import os

    # 填入SMTP账户信息
    # 注意！最好避免在源代码中出现敏感信息。
    # 建议将SMTP账户信息设置在$SMTP_HOST等环境变量中。
    YOUR_SMTP_HOST = '' or os.environ.get('SMTP_HOST')
    YOUR_SMTP_USER = '' or os.environ.get('SMTP_USER')
    YOUR_SMTP_PASS = '' or os.environ.get('SMTP_PASS')

    MAILMAN = Mailman(host=YOUR_SMTP_HOST,
                      user=YOUR_SMTP_USER,
                      password=YOUR_SMTP_PASS)
    print(MAILMAN)
    if not MAILMAN.ready:
        print('邮件服务器连接或登录异常')
    elif MAILMAN.send(sender='7176466@qq.com',
                      receivers=['7176466@qq.com'],
                      subject='Hello, World!',
                      content='你好，世界！'):
        print('邮件发送成功')
    else:
        print('邮件发送失败')
