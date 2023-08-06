包包简介
========

虽然我一度坚守着 Python2，但如今我也离她而去了。

所以，我推荐大家和我一样将 **Python3.5** 作为学习和使用 Python 的起点，所以本包包仅发布了 Python3 的版本。

可能您会觉得这个包包里面的东西五花八门，但我真心希望其中的某些代码对您有用。

安装升级
========

.. code:: shell

    $ pip install --user -U zhao

如何使用
========

用 zhao.xin_email.MailMan 发送邮件

注：为了避免在源代码中出现敏感信息，建议将SMTP账户信息写在$SMTP_HOST等环境变量中。

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

如果您可能也使用 **小米路由器** ，可能您也发现它会不时掉线，只有手动断开ADSL并重新拨号才能恢复上网？

那么，您可以试试 **zhao.xin_api.MiWiFi** 对象，在自己家的服务器上编写一个脚本，并设为每分钟执行一次的计划任务，让它免除您掉线的烦恼。

.. code:: python

    from zhao.xin_api import MiWiFi

    MIWIFI = MiWiFi(password='您自己的小米路由器WEB登录密码')

    if MIWIFI.is_offline:
        if MIWIFI.reconnect():
            printf('自动重新拨号成功')
        else:
            printf('自动重新拨号失败')

又或者，您也有百度开发者帐号，想使用 **百度语音API** 进行 **语音识别** 或 **语音合成** ？

那么，您可以试试我包里面的 **zhao.xin_api.BaiduYuyin** 对象。

.. code:: python

    from zhao.xin_api import BaiduYuyin

    baiduyuyin = BaiduYuyin(api_key='您自己的百度开发者API_KEY', secret_key='您自己的百度开发者SECRET_KEY')
    baiduyuyin.tts_setup(speed=3, person=4)
    baiduyuyin.tts(text='我是百度语音的丫丫')

听，百度的小妹声音真甜：）

又或者，你和家人一起算24点？如果遇到难题，可以借助一下 point24_solutions 函数。

.. code:: python

    >>> from zhao.xin_game import point24_solutions
    >>> SOLUTIONS = point24_solutions(3, 2, 8, 8)
    >>> print('\n'.join(SOLUTIONS) if SOLUTIONS else '无解')
    (8 + 8) * 3 / 2 = 24
    (8 - 3 - 2) * 8 = 24
    (8 - 2 - 3) * 8 = 24

更多用途和秘密，有待您的探索 ...

版本更新
========

修改整理中...

