#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""zhao.xin_email 模块提供电子邮件相关的实现
"""

import atexit
import socket
import smtplib
from email.message import EmailMessage


class EmailSender:

    def __init__(self, host, user, password, tls=True):
        self._host = host
        self._user = user
        self._password = password
        self._tls = tls
        self._server = None
        self.connect()
        atexit.register(self.disconnect)

    def disconnect(self):
        try:
            self._server.quit()
        except AttributeError:
            pass

    def connect(self)->bool:
        try:
            self._server = smtplib.SMTP(host=self._host)
            assert self._connected, 'noop got no response.'
            if self._tls:
                assert self._server.starttls() == (220, b'Ready to start TLS'), \
                    'TLS mode failed.'
            assert self._server.login(user=self._user, password=self._password) \
                == (235, b'Authentication successful'), 'login error.'
            # self._server.set_debuglevel(2)
            return True
        except (socket.gaierror, smtplib.SMTPException, AttributeError, AssertionError) as error:
            print('SMTP server connection error:', error)
            return False

    @property
    def _connected(self)->bool:
        try:
            assert self._server and self._server.noop() == (250, b'Ok')
            return True
        except (AttributeError, AssertionError):
            return False

    @property
    def _ready(self)->bool:
        return self._connected or self.connect()

    def send(self, sender: str, receivers: (str, tuple, list, set), subject: str, content: str)->bool:
        success = False
        if self._ready:
            message = EmailMessage()
            message['From'] = sender
            message['To'] = receivers if isinstance(receivers, str) else ';'.join(receivers)
            message['Subject'] = subject
            message.set_content(content)
            success = self._server.send_message(message) == {}
        return success


if __name__ == '__main__':
    import os
    MAILMAN = EmailSender(host=os.environ.get('SMTP_HOST'),
                          user=os.environ.get('SMTP_USER'),
                          password=os.environ.get('SMTP_PASS'))
    MAILMAN.send(sender='7176466@qq.com',
                 receivers='7176466@qq.com',
                 subject='Hello, World!',
                 content='你好，世界！')
