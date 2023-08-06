包包简介
========

虽然我一度坚守着 Python2，但如今我也离她而去了。

所以，我推荐大家和我一样将 Python3 作为学习和使用 Python 的起点，本包包也仅发布了 Python3 的版本。

可能您会觉得这个包包里面的东西五花八门，但我真心希望其中的某些代码对您有用。

安装升级
========

.. code:: shell

    $ pip install --user -U zhao

如何使用
========

用 zhao.xin_email.Mailman 发送带附件的纯文本邮件

.. code:: python

    import os
    from zhao.xin_email import Mailman

    # 建议将SMTP账户信息设置在$SMTP_HOST等环境变量中。
    YOUR_SMTP_HOST = '' or os.environ.get('SMTP_HOST')
    YOUR_SMTP_USER = '' or os.environ.get('SMTP_USER')
    YOUR_SMTP_PASS = '' or os.environ.get('SMTP_PASS')

    mailman = Mailman(host=YOUR_SMTP_HOST,
                      user=YOUR_SMTP_USER,
                      password=YOUR_SMTP_PASS)

    if not mailman.ready:
        print('邮件服务器连接或登录异常')
    elif mailman.sendmail(sender='7176466@qq.com',
                          receivers=['7176466@qq.com'],
                          subject='Hello, World!',
                          content='你好，世界！',
                          files=[__file__]):  # e.g. ['/home/user/Pictures/image.jpg', ... ]
        print('邮件发送成功')
    else:
        print('邮件发送失败')

更多用途和秘密，有待您的探索 ...

更新历史
========

v0.0.67
--------

时间: 2018-03-27

更新: 为 zhao.xin_email.Mailman.sendmail() 添加 cc, bcc, 发送附件等功能

v0.0.62
--------

时间: 2018-03-27

更新: 添加 zhao.xin_email 模块


