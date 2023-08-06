#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""本模块提供PostgreSQL数据库连接类
"""

__author__ = 'Zhao Xin <7176466@qq.com>'
__copyright__ = 'All Rights Reserved © 1975-2018 Zhao Xin'
__license__ = 'GNU General Public License v3 (GPLv3)'
__version__ = '2018-03-26'
__all__ = ['XinPostgreSQL']

import re
import os

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print('本模块需要 psycopg2-binary 模块的支持，请安装它。\n'
          '运行: pip3 install --user psycopg2-binary')


class XinPostgreSQL(object):
    '''PostgreSQL for Human

    Usage:
    >>> DB = XinPostgreSQL(host='localhost',
                           user='username',
                           password='password',
                           database='database',
                           sql="""DROP TABLE IF EXISTS account;
                                  CREATE TABLE IF NOT EXISTS account (
                                        name TEXT,
                                        money MONEY check (money >= 0.0::MONEY),
                                        PRIMARY KEY (name)
                                  );""")
    >>> print("database connected" if DB else "database connection error")
    database connected
    >>> DB.execute("INSERT INTO account VALUES (%(name)s, %(money)s);", name="tom", money=100.0)
    1
    >>> DB.execute("INSERT INTO account VALUES (%(name)s, %(money)s);", name="jerry", money=100.0)
    1
    >>> DB.query("SELECT * FROM account;")
    [{'money': '$100.00', 'name': 'tom'}, {'money': '$100.00', 'name': 'jerry'}]
    >>> DB.execute("""UPDATE account SET money = money - %(money)s::money WHERE name = %(payer)s;
                      UPDATE account SET money = money + %(money)s::money WHERE name = %(beneficiary)s;""",
                   rowcount=2, payer="tom", beneficiary="jerry", money=50.0)
    2
    >>> DB.query("SELECT * FROM account;")  # after transfer $50 from tom to jerry
    [{'money': '$50.00', 'name': 'tom'}, {'money': '$150.00', 'name': 'jerry'}]
    >>> DB.execute("""UPDATE account SET money = money - %(money)s::money WHERE name = %(payer)s;
                      UPDATE account SET money = money + %(money)s::money WHERE name = %(beneficiary)s;""",
                   rowcount=2, payer="tom", beneficiary="jerry", money=100.0)  # try transfer another $100
    0
    >>> # tom short of money, transfer should failed and transaction should rollback
    >>> DB.query("SELECT * FROM account WHERE name='tom';", fetch=1)  # will tom's money be -$50?
    {'money': '$50.00', 'name': 'tom'}
    >>> DB.query("SELECT * FROM account WHERE name='jerry';", fetch=1)
    {'money': '$150.00', 'name': 'jerry'}
    >>> DB.query("SELECT * FROM account WHERE name='nobody';", fetch=1)
    {}
    >>> [account['name'] for account in DATABASE.query("SELECT name FROM account;")]
    ['tom', 'jerry']
    '''

    def __init__(self, sql='', **kwargs):
        """
        参数 sql:
            以分号分隔和结束的多条 SQL 语句，在实例化对象时被执行，可被用作作创建数据表。
        参数 kwargs：
            可含有 host, user, password, database 等
        """
        self._conn = None
        try:
            self._conn = psycopg2.connect(host=kwargs.get('host') or os.environ.get('POSTGRESQL_HOST'),
                                          user=kwargs.get('user') or os.environ.get('POSTGRESQL_USER'),
                                          password=kwargs.get('password') or os.environ.get('POSTGRESQL_PASS'),
                                          database=kwargs.get('database') or os.environ.get('POSTGRESQL_BASE'),
                                          cursor_factory=psycopg2.extras.DictCursor)
            (sql == '') or self.execute(sql)
        except psycopg2.Error:
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
        with self._conn, self._conn.cursor() as psql:
            realcount = 0
            try:
                for _sql in re.findall(r'[^;]+;', sql, re.S):
                    psql.execute(_sql, kwargs)
                    realcount += psql.rowcount
                assert rowcount <= 0 or rowcount == realcount
            except (psycopg2.Error, AssertionError, KeyError):
                pass
            return realcount

    def executemany(self, sql, argslist, rowcount=0):
        """原子地以 executemany 方式执行多条 SQL 语句
        参数 sql:
            以分号分隔和结束的多条 SQL 语句，将以 records 作为参数被逐条执行。
        参数 records:
            含数据字典的可迭代对象
        参数 rowcount:
            若设置为 > 0的数，执行SQL语句后将检查实际修改行数realcount，若不等于rowcount，则回滚！
        """
        with self._conn, self._conn.cursor() as psql:
            realcount = 0
            try:
                for _sql in re.findall(r'[^;]+;', sql, re.S):
                    psql.executemany(sql, argslist)
                    realcount += psql.rowcount
                assert rowcount <= 0 or rowcount == realcount
            except (psycopg2.Error, AssertionError, KeyError):
                pass
            return realcount

    def query(self, sql, fetch=0, **kwargs):
        with self._conn, self._conn.cursor() as psql:
            try:
                psql.execute(sql, kwargs)
                return (dict(psql.fetchone() or {}) if fetch == 1 else
                        list(map(dict, psql.fetchmany(fetch) if fetch > 1 else psql.fetchall())))
            except (psycopg2.Error, AssertionError, KeyError):
                return {} if fetch == 1 else []
