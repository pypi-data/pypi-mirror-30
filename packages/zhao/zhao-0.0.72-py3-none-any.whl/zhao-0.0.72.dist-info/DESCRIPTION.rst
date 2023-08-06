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

用zhao.xin_email.Mailman 发送带附件的邮件

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

简单好用的 SQLite 类 XinSQLite

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

v0.0.72
--------

时间: 2018-03-28

 - 添加: xin_sqlite 模块
 - 添加: xin_postgresql 模块

v0.0.71
--------

时间: 2018-03-28

 - 更新: 为 xin_email.Mailman.sendmail() 添加 cc, bcc, 发送附件等功能

v0.0.62
--------

时间: 2018-03-27

 - 添加: xin_email 模块


