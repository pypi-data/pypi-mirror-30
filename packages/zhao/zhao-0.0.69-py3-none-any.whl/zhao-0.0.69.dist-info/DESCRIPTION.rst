包包简介
========

本包包之所以仅发布了 Python3 的版本，是因为一度坚守着 Python2 的我如今也开了。

现在，我只会推荐大家和我一样将 Python3 作为学习和使用 Python 的起点。

这个包包里的东西，是我准备写给自己用的一些小玩意，您可能会觉得有点五花八门，但我真心希望其中的某些代码对您有用（使用说明中提到的内容尤其值得您的信奈）。

安装升级
========

.. code:: shell

    $ pip install --user -U zhao

使用说明
========

用 zhao.xin_email.Mailman 发送带附件的邮件

.. code:: python

    from zhao.xin_email import Mailman
    mailman = Mailman(host='YOUR_SMTP_HOST',
                      user='YOUR_SMTP_USER',
                      password='YOUR_SMTP_PASS')

    if mailman.sendmail(sender='youname@example.com',
                        receivers=['tom@gmail.com', 'jerry@hotmail.com'],
                        subject='Hello, World!',
                        content='你好，世界！',
                        cc=['superman@sina.com'],
                        bcc=['boos@haven.com'],
                        files=[__file__]):
        print('邮件发送成功')
    else:
        print('邮件发送失败')

更多用途和秘密，有待您的探索 ...

更新历史
========

v0.0.69
--------

时间: 2018-03-28

更新: 为 zhao.xin_email.Mailman.sendmail() 添加 cc, bcc, 发送附件等功能

v0.0.62
--------

时间: 2018-03-27

更新: 添加 zhao.xin_email 模块


