#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""本模块提供基本的正则表达式相关的实现
"""

import re


def regex_pattern(regex, mode=(re.I | re.S | re.X)):
    return re.compile(regex, mode)


REGEX_0_TO_255 = r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)'
REGEX_ANY_NUMBER = r'(?:[0-9]+)'
REGEX_FOUR_OPERATORS = r'(?:[-+*/]|÷|×)'
REGEX_IPV4 = r'(?:{0}\.{0}\.{0}\.{0})'.format(REGEX_0_TO_255)
