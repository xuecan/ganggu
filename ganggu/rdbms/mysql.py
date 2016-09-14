# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
# Tools for MySQL with SQLAlchemy

Requirement:

* SQLAlchemy
* PyMySQL
"""

__all__ = [
    'Schema', 'col', 'pkey', 'pkeys', 'fkey', 'idx', 'uniq', 'NULL', 'NOTNULL',
    'make_engine'
]

from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import INTEGER
from .schema import Schema, col, pkeys, fkeys, idx, uniq, NULL, NOTNULL
from .schema import pkey as _pkey, fkey as _fkey


def make_engine(uri, debug=False):
    if not uri.startswith("mysql+pymysql://"):
        raise ValueError("not for MySQL")
    engine = create_engine(
        uri,
        encoding="utf-8",
        paramstyle="pyformat",
        isolation_level="READ COMMITTED",
        echo=debug
    )
    return engine


def pkey(name="id", type_=None, **kwargs):
    """构建主键列"""
    if type_ is None:
        type_ = INTEGER(unsigned=True)
        kwargs.setdefault('autoincrement', True)
    return _pkey(name, type_, **kwargs)


def fkey(table, col_name="id", type_=None, onupdate='CASCADE', ondelete='RESTRICT', primary_key=False):
    """构建外键列"""
    if type_ is None:
        type_ = INTEGER(unsigned=True)
    return _fkey(table, col_name, type_, onupdate, ondelete, primary_key)
