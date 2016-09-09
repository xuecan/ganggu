# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
一组方便构建基于 SQLAlchemy 数据库定义的工具。
"""


__all__ = ["table", "col", "pkey", "pkeys", "fkey", "idx", "uniq",
           "NULL", "NOTNULL",
           'Database']


from sqlalchemy import \
    MetaData, Table, Column, \
    PrimaryKeyConstraint, ForeignKey, Index, UniqueConstraint, \
    INTEGER


# =====================================================================
# 方便构建 schema 的工具
# =====================================================================

class NULL:
    """nullable = True"""


class NOTNULL:
    """nullable = False"""


class Schema(object):

    def __init__(self, metadata=None):
        self.metadata = metadata or MetaData()

    def _build_table(self, tablename, items):
        """构建表对象"""
        args = list()
        kwargs = dict()
        # 读取表的定义
        for item in items:
            if isinstance(item, dict):
                type_ = item["type"]
                if type_ == "index":
                    columns = item["columns"]
                    name = "idx_%s__%s" % (tablename, "__".join(columns))
                    item = Index(name, *columns)
                elif type_ == "unique":
                    columns = item["columns"]
                    name = "uniq_%s__%s" % (tablename, "__".join(columns))
                    item = UniqueConstraint(*columns, name=name)
                elif type_ == "primary":
                    columns = item["columns"]
                    name = "pkey_%s__%s" % (tablename, "__".join(columns))
                    item = PrimaryKeyConstraint(*columns, name=name)
                else:
                    raise ValueError("unsupported schema item")
                args.append(item)
            elif isinstance(item, tuple):
                k, v = item
                kwargs[k] = v
            else:
                args.append(item)
        instance = Table(tablename, self.metadata, *args, **kwargs)
        return instance

    def table(self, func):
        """用于修饰表定义的修饰器。

        用法：

            @table
            def user():
                return [...]

            @table('metadata')
            def table_netadata():
                return [...]
        """
        if isinstance(func, str):
            # 以 @table('tablename') 的形式修饰
            # 等价于 func = table('tablename')(func)
            tablename = func
            def outter(func):
                def inner():
                    items = func()
                    return self._build_table(tablename, items)
                return inner
            return outter()
        else:
            # 以 @table 的形式修饰
            # 等价于 func = table(func)
            def wrapper():
                tablename = func.__name__
                items = func()
                return self._build_table(tablename, items)
            return wrapper()


def col(*args, **kwargs):
    """用于构建列，返回 sqlalchemy.Column 实例"""
    args = list(args)
    if args.count(NULL) + args.count(NOTNULL) > 1:
        raise ValueError("a column must be either NULL-able or NOTNULL")
    if NOTNULL in args:
        args.remove(NOTNULL)
        kwargs["nullable"] = False
    if NULL in args:
        args.remove(NULL)
        kwargs["nullable"] = True
    return Column(*args, **kwargs)


def pkey(name="id", type_=None, **kwargs):
    """构建主键列"""
    if type_ is None:
        type_ = INTEGER
        kwargs.setdefault('autoincrement', True)
    return Column(name, type_, nullable=False, primary_key=True, **kwargs)


def pkeys(*columns):
    """返回用于将多个列构建为主键的信息"""
    return {"type": "primary", "columns": columns}


def fkey(table, col_name="id", type_=None, onupdate='CASCADE', ondelete='RESTRICT', primary_key=False):
    """构建外键列"""
    name = "%s_%s" % (table, col_name)
    foreign = "%s.%s" % (table, col_name)
    if type_ is None:
        type_ = INTEGER
    return Column(name, type_,
                  ForeignKey(foreign, onupdate=onupdate, ondelete=ondelete),
                  primary_key=primary_key,
                  nullable=False)


def idx(*columns):
    """返回让 table 构建普通索引的信息"""
    return {"type": "index", "columns": columns}


def uniq(*columns):
    """返回让 table 构建唯一索引的信息"""
    return {"type": "unique", "columns": columns}
