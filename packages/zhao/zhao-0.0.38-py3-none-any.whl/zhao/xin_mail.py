#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""zhao.xin_mail module
"""

__version__ = '2018-03-25'
__license__ = 'GPLv3'
__author__ = 'Zhao Xin <7176466@qq.com>'
__copyright__ = 'All rights reserved © 1975-2018 Zhao Xin'

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


def send_email(sender, subject, content, receivers):
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


print(send_email('7176466@qq.com', '2018-03-26 09:26:52', '2018-03-26 09:26:57content', '7176466@qq.com'))
