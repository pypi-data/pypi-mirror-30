#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""zhao.xin_postgresql module
"""

__version__ = '2018-03-24'
__license__ = 'GPLv3'
__author__ = 'Zhao Xin <7176466@qq.com>'
__copyright__ = 'All rights reserved © 1975-2018 Zhao Xin'

import re
import os
import psycopg2
import psycopg2.extras


class XinPostgreSQL(object):
    '''PostgreSQL for Human

    Usage:
    >>> DB = XinPostgreSQL(sql="""DROP TABLE IF EXISTS account;
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
        self._conn = None
        try:
            self._conn = psycopg2.connect(host=kwargs.get('host') or os.environ.get('POSTGRESQL_HOST'),
                                          user=kwargs.get('user') or os.environ.get('POSTGRESQL_USER'),
                                          password=kwargs.get('password') or os.environ.get('POSTGRESQL_PASS'),
                                          database=kwargs.get('database') or os.environ.get('POSTGRESQL_BASE'),
                                          cursor_factory=psycopg2.extras.DictCursor)
            sql == '' or self.execute(sql)
        except (psycopg2.Error, AssertionError):
            pass

    def __del__(self):
        self._conn and self._conn.close()

    def __bool__(self):
        return bool(self._conn)

    def __enter__(self):
        return self._conn

    def execute(self, sql, rowcount=0, **kwargs):
        with self._conn, self._conn.cursor() as psql:
            realcount = 0
            try:
                for _sql in re.findall(r'[^\s].+?;', sql, re.S):
                    psql.execute(_sql, kwargs)
                    realcount += psql.rowcount
                assert rowcount <= 0 or rowcount == realcount
            except (psycopg2.Error, AssertionError):
                pass
            return realcount

    def executemany(self, sql, argslist, rowcount=0):
        with self._conn, self._conn.cursor() as psql:
            try:
                psql.execute(sql, argslist)
                assert rowcount <= 0 or rowcount == psql.rowcount
            except (psycopg2.Error, AssertionError):
                pass
            return psql.rowcount

    def query(self, sql, fetch=0, **kwargs):
        with self._conn, self._conn.cursor() as psql:
            try:
                psql.execute(sql, kwargs)
                return (dict(psql.fetchone() or {}) if fetch == 1 else
                        list(map(dict, psql.fetchmany(fetch) if fetch > 1 else psql.fetchall())))
            except psycopg2.Error:
                return {} if fetch == 1 else []
