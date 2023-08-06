包包简介
========

虽然我一度坚守着 `Python2`，但如今我也离她而去了。

所以，我推荐大家和我一样将 **`Python3.5`** 作为学习和使用 Python 的起点，所以本包包仅发布了 `Python3` 的版本。

可能您会觉得这个包包里面的东西五花八门，但我真心希望其中的某些代码对您有用。

安装升级
========

.. code:: shell

    $ pip install --user -U zhao

如何使用
========

用 `zhao.xin_email.MailMan` 发送邮件 (暂时仅支持不带附件的纯文本邮件)

.. code:: python

    import os
    from zhao.xin_email import MailMan

    # 填入SMTP账户信息
    # 注意！最好避免在源代码中出现敏感信息。
    # 建议将SMTP账户信息设置在$SMTP_HOST等环境变量中。
    YOUR_SMTP_HOST = '' or os.environ.get('SMTP_HOST')
    YOUR_SMTP_USER = '' or os.environ.get('SMTP_USER')
    YOUR_SMTP_PASS = '' or os.environ.get('SMTP_PASS')

    MAILMAN = MailMan(host=YOUR_SMTP_HOST,
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

更多用途和秘密，有待您的探索 ...

版本更新
========

修改整理中...

