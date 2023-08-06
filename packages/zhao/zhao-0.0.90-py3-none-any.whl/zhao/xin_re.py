#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""本模块提供基本的正则表达式相关的实现
"""

import re


def regex_pattern(regex, mode=(re.I | re.S | re.X)):
    return re.compile(regex, mode)


REGEX_000_TO_255 = r'(?:[01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])'
REGEX_ANY_NUMBER = r'(?:[0-9]+)'
REGEX_FOUR_OPERATORS = r'(?:[-+*/]|÷|×)'
REGEX_IPV4 = r'(?:{0}\.{0}\.{0}\.{0})'.format(REGEX_000_TO_255)
