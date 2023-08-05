# -*- coding: utf-8 -*-
"""zhao.xin_net.url

See
    - RFC3986 aka. STD66 (2005)
    - IANA schemes http://www.iana.org/assignments/uri-schemes.html

scheme:[//[user[:password]@]host[:port]][/path][?query][#fragment]
"""

import re
import urllib

UNICODE_SRE = re.compile(r'\u00A1-\uFFFF')                          # UNICODE范围
URI_SCHEME_SRE = re.compile(r'(?:([A-Za-z][[A-Za-z\d\+\-\.]*):)')   # “URI协议”
URI_PORT_SRE = re.compile(r'(?::(\d{2,5}))')
URI_FRAGMENT_SRE = re.compile(r'(?:#(\S*)?)')
IPV6_SRE = re.compile(r'\[[0-9a-f:\.]+\]')  # (simple regex, validated later)


class URL(object):
    """统一资源定位符 Uniform Resource Locator"""

    PATTERN = re.compile(r'(?:([A-Za-z][[A-Za-z\d\+\-\.]*):)'
                         r'(?://)?'
                         r'[^\s/?#]+?'
                         r'([^\s?#]*)?'
                         r'(?:\?([^\s#]*)?)?'
                         r'(?:#(\S*)?)?', re.IGNORECASE)

    def __new__(cls, string):
        if not URL.PATTERN.match(string):
            return None
        self = super(URL, cls).__new__(cls)
        (self.scheme, self.netloc, self.path,
         self.params, self.query, self.fragment) = result = urllib.parse(string)
        self.username = result.username
        self.password = result.password
        self.hostname = result.hostname
        self.port = result.port
        self.filename = result.path.split('/')[-1]
        self.query = urllib.parse.parse_qs(self.query)
        return self
