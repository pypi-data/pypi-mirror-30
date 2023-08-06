#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""zhao.xin_email 模块提供电子邮件相关的实现
"""

import os
import re
import atexit
import socket
import smtplib
import mimetypes
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

__all__ = ['Mailman']

_EMAIL_ADDR_REGEX_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I | re.S | re.X)


def _all_email_addresses_from(obj):
    return ', '.join(match.group() for match in _EMAIL_ADDR_REGEX_PATTERN.finditer(str(obj)))


def _enveloping(sender, receivers, subject, content, **kwargs):
    # 构造邮件头部及纯文本正文部分
    mail = MIMEMultipart()
    mail['From'] = sender
    mail['To'] = _all_email_addresses_from(receivers)
    if 'cc' in kwargs:
        mail['CC'] = _all_email_addresses_from(kwargs.get('cc', ''))
    if 'bcc' in kwargs:
        mail['BCC'] = _all_email_addresses_from(kwargs.get('bcc', ''))
    mail['Subject'] = subject
    mail.attach(MIMEText(content))

    # 构造邮件附件部分
    for file_path in kwargs.get('files', []):
        if os.access(file_path, os.R_OK):
            mimetype, _encoding = mimetypes.guess_type(file_path)
            maintype, subtype = ('application', 'octet-stream') if mimetype is None else mimetype.split('/', 1)
            with open(file_path, 'r' if maintype == 'text' else 'rb') as attach:
                mimepart = {'text': MIMEText, 'image': MIMEImage, 'audio': MIMEAudio,
                            'application': MIMEApplication}.get(maintype, MIMEApplication)(attach.read(), subtype)
                mimepart.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
                mail.attach(mimepart)

    return mail


class Mailman:
    """电子邮件类

    创建: Mailman(host, user, password, tls=True)
    属性: bool ready，标志与SMTP服务器连接、登录状态均正常。
    方法: bool sendmail(sender, receivers, subject, content, **kwargs)，用于发送邮件，返回True表示发送成功。
         字典参数 kwargs 中可以包含: cc 不限类型, bcc 不限类型, files 字符串列表(附件文件路径列表)

    示例: 建议将SMTP账户信息设置在$SMTP_HOST等环境变量中。
        mailman = Mailman(host=os.environ.get('SMTP_HOST'),
                        user=os.environ.get('SMTP_USER'),
                        password=os.environ.get('SMTP_PASS'))
        if not mailman.ready:
            print('邮件服务器连接或登录异常')
        elif mailman.sendmail(sender='youname@example.com',
                              receivers=['tom@gmail.com', 'jerry@hotmail.com'],
                              subject='Hello, World!',
                              content='你好，世界！',
                              cc=['superman@sina.com'],
                              bcc=['boos@haven.com'],
                              files=[__file__]):
            print('邮件发送成功')
        else:
            print('邮件发送失败')
    """

    def __init__(self, host, user, password, tls=True):
        self._host = host
        self._user = user
        self._password = password
        self._tls = tls
        self._server = None
        self.connect()
        atexit.register(self.disconnect)
        self.send = self.sendmail

    def __str__(self):
        return 'Mailman: Host=%r, User=%r, Password=%r, TLS=%r, Ready=%r' % (self._host, self._user,
                                                                             '******' if bool(self._password) else None,
                                                                             self._tls, self.ready)

    def disconnect(self):
        try:
            self._server.quit()
        except (socket.gaierror, smtplib.SMTPException, AttributeError):
            pass

    def connect(self)->bool:
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
        return self._connected or self.connect()

    def sendmail(self, sender: str, receivers, subject: str, content: str, **kwargs)->bool:
        success = False
        if self.ready:
            mail = _enveloping(sender, receivers, subject, content, **kwargs)
            success = self._server.send_message(mail) == {}
        return success
