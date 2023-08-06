包包简介
========

本包包之所以仅发布了 Python3 的版本，是因为一度坚守着 Python2 的我如今也转到3了。而且，我要推荐大家将 Python3 作为您学习和使用 Python 的起点。

这个包包里的东西是我准备写给自己用的一些小玩意，您可能会觉得有点五花八门，但我真心希望其中的某些代码对您也有用（使用说明中提到的内容尤其值得您的信奈）。

安装升级
========

.. code:: shell

    $ pip3 install --user -U zhao

使用说明
========

百度语音API
----------------

通过 zhao.xin_api.BaiduYuyin 对象，使用百度语音API进行语音识别或语音合成:

.. code:: python

    from zhao.xin_api.baiduyuyin import BaiduYuyin

    yaya = BaiduYuyin(api_key='您自己的百度开发者API_KEY',
                      secret_key='您自己的百度开发者SECRET_KEY')
    yaya.tts_setup(speed=3, person=4)
    yaya.tts('我是百度语音的丫丫', save='yaya.mp3')

听，百度的小妹声音真甜：）

小米路由器API
----------------

如果您可能也使用小米路由器 ，可能您也发现它会不时掉线，只有手动断开ADSL并重新拨号才能恢复上网？

那么，您可以试试 zhao.xin_api.miwifi.MiWiFi 对象，在自己家的服务器上编写一个脚本，并设为每分钟执行一次的计划任务，让它免除您掉线的烦恼。

.. code:: python

    from zhao.xin_api.miwifi import MiWiFi

    MIWIFI = MiWiFi(password='您自己的小米路由器WEB登录密码')

    if MIWIFI.is_offline:
        if MIWIFI.reconnect():
            printf('自动重新拨号成功')
        else:
            printf('自动重新拨号失败')


用 zhao.xin_email.Mailman 发送带附件的邮件
------------------------------------------------

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

简单好用的数据库类 XinSQLite
------------------------------------------------

.. code:: python

    >>> from zhao.xin_sqlite import XinSQLite
    >>> DB = XinSQLite(sql='CREATE TABLE language (name text, year integer);')
    >>> DB.execute('insert into language values (:name, :year);', name='C', year=1972)
    1
    >>> DB.executemany('insert into language values (:name, :year);', [dict(name='Python', year=1991),
                                                                       dict(name='Go',     year=2009)])
    2
    >>> DB.query('select count(*) as total from language;', fetch=1).get('total', 0)
    3
    >>> DB.query('select * from language where name=:name limit 1;', fetch=1, name='Ruby')
    {}
    >>> DB.query('select * from language where name=:name limit 1;', fetch=1, name='Python')
    {'year': 1991, 'name': 'Python'}
    >>> for row in DB.query('select name, year from language;'): print(row)
    {'year': 1972, 'name': 'C'}
    {'year': 1991, 'name': 'Python'}
    {'year': 2009, 'name': 'Go'}

更多用途和秘密，有待您的探索 ...

更新历史
========

v0.0.91
--------

时间: 2018-04-11

 - 添加: xin_os 模块的几个新函数

v0.0.87
--------

时间: 2018-03-29

 - 添加: xin_api 包
 - 添加: xin_api.baiduyuyin 模块
 - 添加: xin_api.miwifi 模块

v0.0.80
--------

时间: 2018-03-28

 - 添加: xin_os 模块
 - 添加: xin_re 模块
 - 添加: xin_net 模块
 - 添加: xin_audio 模块
 - 添加: xin_sqlite 模块
 - 添加: xin_postgresql 模块
 - 更新: 为 xin_email.Mailman.sendmail() 添加 cc, bcc, 发送附件等功能

v0.0.62
--------

时间: 2018-03-27

 - 添加: xin_email 模块


