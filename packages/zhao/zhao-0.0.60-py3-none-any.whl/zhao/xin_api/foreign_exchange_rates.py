# -*- coding: utf-8 -*-
"""外汇交易汇率API
"""

import requests


class ForeignExchangeRates(object):
    """外汇交易汇率API

    使用方法:
        >>> from zhao.xin_api import ForeignExchangeRates
        >>> FERS = ForeignExchangeRates()
        >>> for year in range(2015, 2018):
                FERS.date = f'{year}-12-28'
                print(FERS.rate('CNY'))
        USD:CNY 1:6.4873 @ 2015-12-28
        USD:CNY 1:6.9593 @ 2016-12-28
        USD:CNY 1:6.536 @ 2017-12-28
        >>> FERS.base = 'CNY'
        >>> print(FERS.rate('JPY'))
        CNY:JPY 1:17.274 @ 2017-12-28
    """

    def __init__(self, base='USD'):
        self.session = requests.Session()
        self._date = 'latest'  # 最新的数据是昨天的
        self._base = base
        self._rates = {'ATS': -1.0,  # 奥地利先令
                       'AUD': -1.0,  # 澳元
                       'BEF': -1.0,  # 比利时法郎
                       'BGN': -1.0,  # 保加利亚列弗
                       'BRL': -1.0,  # 巴西雷亚尔
                       'CAD': -1.0,  # 加拿大元
                       'CHF': -1.0,  # 瑞士法郎
                       'CNY': -1.0,  # 人民币
                       'CZK': -1.0,  # 捷克克朗
                       'DKK': -1.0,  # 丹麦克朗
                       'ESP': -1.0,  # 西班牙比塞塔
                       'EUR': -1.0,  # 欧元
                       'FRF': -1.0,  # 法国法郎
                       'GBP': -1.0,  # 英镑
                       'HKD': -1.0,  # 港币
                       'HRK': -1.0,  # 克罗地亚库纳
                       'HUF': -1.0,  # 匈牙利福林
                       'IDR': -1.0,  # 印尼卢比
                       'IEP': -1.0,  # 爱尔兰镑
                       'ILS': -1.0,  # 以色列新锡克尔
                       'ITL': -1.0,  # 意大利里拉
                       'INR': -1.0,  # 印度卢比
                       'JPY': -1.0,  # 日元
                       'KRW': -1.0,  # 韩元
                       'LUF': -1.0,  # 卢森堡法郎
                       'MXN': -1.0,  # 墨西哥元
                       'MYR': -1.0,  # 马来西亚林吉特
                       'NLG': -1.0,  # 荷兰盾
                       'NOK': -1.0,  # 挪威克朗
                       'NZD': -1.0,  # 新西兰元
                       'PHP': -1.0,  # 菲律宾比索
                       'PLN': -1.0,  # 波兰兹罗提
                       'PTE': -1.0,  # 葡萄牙埃斯库多
                       'RON': -1.0,  # 罗马尼亚列伊
                       'RUB': -1.0,  # 俄罗斯卢布
                       'SEK': -1.0,  # 瑞典克朗
                       'SGD': -1.0,  # 新加坡元
                       'THB': -1.0,  # 泰铢
                       'TRY': -1.0,  # 土耳其里拉
                       'USD': -1.0,  # 美元
                       'ZAR': -1.0}  # 南非兰特
        self._update()

    def _update(self):
        api_url = f'https://api.fixer.io/{self._date}?base={self._base}'
        response = self.session.get(api_url)
        self._date = 'N/A'
        self.rates = self._rates.copy()
        if response.ok:
            data = response.json()
            self._date = data['date']
            self.rates.update(data['rates'])

    @property
    def date(self):
        "汇率日期"
        return self._date

    @date.setter
    def date(self, date):
        if self._date != date:
            self._date = date
            self._update()

    @property
    def base(self):
        "基础货币"
        return self._base

    @base.setter
    def base(self, base):
        if self._base != base:
            self._base = base
            self._update()

    def rate(self, code):
        "二级货币的汇率"
        return f'{self.base}:{code} 1:{self.rates.get(code, -1.0)} @ {self.date}'
