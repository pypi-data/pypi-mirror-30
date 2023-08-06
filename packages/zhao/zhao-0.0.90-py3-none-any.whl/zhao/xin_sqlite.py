# -*- coding:utf-8 -*-
"""本模块提供SQLite数据库连接类
"""

__author__ = 'Zhao Xin <7176466@qq.com>'
__copyright__ = 'All Rights Reserved © 1975-2018 Zhao Xin'
__license__ = 'GNU General Public License v3 (GPLv3)'
__version__ = '2018-03-26'
__all__ = ['XinSQLite']

import re
import sqlite3


class XinSQLite(object):
    """SQLite for Human

    Usage:
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
    """

    def __init__(self, path=':memory:', sql=''):
        """
        参数 sql:
            以分号分隔和结束的多条 SQL 语句，在实例化对象时被执行，可被用作作创建数据表。
        """
        self._conn = None
        try:
            self._conn = sqlite3.connect(path)
            self._conn.row_factory = sqlite3.Row
            (sql == '') or self.execute(sql)
        except sqlite3.Error:
            pass

    def __del__(self):
        self._conn and self._conn.close()

    def __bool__(self):
        return bool(self._conn)

    def execute(self, sql, rowcount=0, **kwargs):
        """原子地执行多条 SQL 语句
        参数 sql:
            以分号分隔和结束的多条 SQL 语句，将以 kwargs 作为参数被逐条执行。
        参数 rowcount:
            若设置为>0的数，执行SQL语句后将检查实际修改行数realcount，若不等于rowcount，则回滚！
        """
        with self._conn:
            realcount = 0
            try:
                for _sql in re.findall(r'[^;]+;', sql, re.S):
                    realcount += self._conn.execute(_sql, kwargs).rowcount
                assert rowcount <= 0 or rowcount == realcount
            except (sqlite3.Error, AssertionError, KeyError):
                pass
            return realcount

    def executemany(self, sql, records, rowcount=0):
        """原子地以 executemany 方式执行多条 SQL 语句
        参数 sql:
            以分号分隔和结束的多条 SQL 语句，将以 records 作为参数被逐条执行。
        参数 records:
            含数据字典的可迭代对象
        参数 rowcount:
            若设置为>0的数，执行SQL语句后将检查实际修改行数realcount，若不等于rowcount，则回滚！
        """
        with self._conn:
            realcount = 0
            try:
                for _sql in re.findall(r'[^;]+;', sql, re.S):
                    realcount += self._conn.executemany(_sql, records).rowcount
                assert rowcount <= 0 or rowcount == realcount
            except (sqlite3.Error, AssertionError, KeyError):
                pass
            return realcount

    def query(self, sql, fetch=0, **kwargs):
        with self._conn:
            try:
                result = self._conn.execute(sql, kwargs)
                return (dict(result.fetchone() or {}) if fetch == 1 else
                        list(map(dict, result.fetchmany(fetch) if fetch > 1 else result.fetchall())))
            except (sqlite3.Error, AssertionError, KeyError):
                return {} if fetch == 1 else []
