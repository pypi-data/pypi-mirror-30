# -*- coding:utf-8 -*-
"""zhao.xin_email 模块提供电子邮件相关的实现
"""

__author__ = 'Zhao Xin<7176466@qq.com>'
__copyright__ = 'All Rights Reserved © 1975-2018 Zhao Xin'
__license__ = 'GNU General Public License v3 (GPLv3)'
__version__ = '2018-03-26'

import os
import atexit
import smtplib
from email.message import EmailMessage


try:
    SMTP = smtplib.SMTP(host=os.environ.get('QQ_SMTP_HOST'))
    SMTP.ehlo()
    SMTP.starttls()
    SMTP.login(user=os.environ.get('QQ_SMTP_USER',),
               password=os.environ.get('QQ_SMTP_PASS'))
    atexit.register(SMTP.close)
except smtplib.SMTPException:
    SMTP = None


def send_email(sender: str, subject, content, receivers):
    try:
        assert sender, 'sender email error'
        assert subject, 'email subject error'
        assert content, 'email content error'
        assert receivers, 'email receivers error'
        assert SMTP, 'email host error'
        message = EmailMessage()
        message['From'] = sender
        message['To'] = receivers
        message['Subject'] = subject
        message.set_content(content)
        SMTP.send_message(message)
        return 'ok'
    except AssertionError as error:
        return error
