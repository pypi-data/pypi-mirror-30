# -*- coding:utf-8 -*-
"""zhao.xin_sqlite module
"""

__author__ = 'Zhao Xin<7176466@qq.com>'
__copyright__ = 'All Rights Reserved © 1975-2018 Zhao Xin'
__license__ = 'GNU General Public License v3 (GPLv3)',
__version__ = '2018-03-26'


import re
import sqlite3


class XinSQLite(object):
    """SQLite for Human

    Usage:
    >>> DB = XinSQLite(sql='create table languages (name text, year integer);')
    >>> DB.execute('insert into languages values (:name, :year);', name='C', year=1972)
    1
    >>> DB.executemany('insert into languages values (:name, :year);', (dict(name='Python', year=1991),
                                                                        dict(name='Go', year=2009)))
    2
    >>> DB.query('select count(*) as total from languages;', fetch=1).get('total')
    3
    >>> DB.query('select * from languages where name=:name limit 1;', fetch=1, name='Python')
    {'year': 1991, 'name': 'Python'}
    >>> for row in DB.query('select name, year from languages;'): print(row)
    {'year': 1972, 'name': 'C'}
    {'year': 1991, 'name': 'Python'}
    {'year': 2009, 'name': 'Go'}
    >>> DB.query('select * from languages where name=:name limit 1;', fetch=1, name='Ruby')
    {}
    """

    def __init__(self, path=':memory:', sql=''):
        self._conn = None
        try:
            self._conn = sqlite3.connect(path)
            self._conn.row_factory = sqlite3.Row
            sql == '' or self.execute(sql)
        except (sqlite3.Error, AssertionError):
            pass

    def __del__(self):
        self._conn and self._conn.close()

    def __bool__(self):
        return bool(self._conn)

    def __enter__(self):
        return self._conn

    def execute(self, sql, rowcount=0, **kwargs):
        with self._conn:
            realcount = 0
            try:
                for _sql in re.findall(r'[^\s].+?;', sql, re.S):
                    realcount += self._conn.execute(_sql, kwargs).rowcount
                assert rowcount <= 0 or rowcount == realcount
            except (sqlite3.Error, AssertionError):
                pass
            return realcount

    def executemany(self, sql, argslist, rowcount=0):
        with self._conn:
            realcount = 0
            try:
                realcount = self._conn.executemany(sql, argslist).rowcount
                assert rowcount <= 0 or rowcount == realcount
            except (sqlite3.Error, AssertionError):
                pass
            return realcount

    def query(self, sql, fetch=0, **kwargs):
        with self._conn:
            try:
                result = self._conn.execute(sql, kwargs)
                return (dict(result.fetchone() or {}) if fetch == 1 else
                        list(map(dict, result.fetchmany(fetch) if fetch > 1 else result.fetchall())))
            except sqlite3.Error:
                return {} if fetch == 1 else []
