# -*- coding: utf-8 -*-
"""zhao.xin_re
该模块提供各类常用的正则表达式
"""

import re

SMALL_INT_PATTERN = r'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)'  # 0~255

IPV4_PATTERN = r'{0}\.{0}\.{0}\.{0}'.format(SMALL_INT_PATTERN)
IPV4_SRE = re.compile(IPV4_PATTERN)
