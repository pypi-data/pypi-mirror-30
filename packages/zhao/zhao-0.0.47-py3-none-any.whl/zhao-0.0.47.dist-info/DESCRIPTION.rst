包包简介
==============

一直以来我坚守着 Python2，但如今我也离她而去了。

现在我推荐大家和我一样将 **Python3.5** 作为学习和使用 Python 的起点。

所以本包包仅发布了 Python3 的版本。

可能您会觉得这个包里面东西五花八门，但我真心希望其中的某些代码对您有用。

比如，如果您可能也使用 **小米路由器** ，可能您也发现它会不时掉线，只有手动断开ADSL并重新拨号才能恢复上网？

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

如何安装或升级
==============

.. code:: shell

    $pip3 install --user -U zhao


版本更新
========

修改整理中...

