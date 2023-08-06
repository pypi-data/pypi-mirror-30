# -*- coding: utf-8 -*-
"""提供基本的正则表达式相关的实现
"""

import re

REGEX_INT_255 = r'25[0-5]|2[0-4]\d|[0-1]?\d?\d'
REGEX_IPV4 = r'(?:{0})\.(?:{0})\.(?:{0})\.(?:{0})'.format(REGEX_INT_255)
PATTERN_IPV4 = re.compile(REGEX_IPV4)
