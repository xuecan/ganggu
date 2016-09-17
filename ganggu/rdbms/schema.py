# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
一组方便构建基于 SQLAlchemy 数据库定义的工具。
"""


__all__ = ['Schema', 'col', 'pkey', 'fkey', 'idx', 'uniq',
           'NULL', 'NOTNULL', 'PRIMARY', 'FOREIGN']


from sqlalchemy import MetaData, Table, Column, \
    PrimaryKeyConstraint, ForeignKeyConstraint, ForeignKey, \
    Index, UniqueConstraint


# =====================================================================
# 方便构建 schema 的工具
# =====================================================================

class NULL:
    """nullable=True"""


class NOTNULL:
    """nullable=False"""


class PRIMARY:
    """primary_key=True"""


def FOREIGN(refname, **kwargs):
    """构建用于 Column 参数的外键描述"""
    kwargs.setdefault('onupdate', 'CASCADE')
    kwargs.setdefault('ondelete', 'RESTRICT')
    return ForeignKey(refname, **kwargs)


class Schema(object):

    def __init__(self, metadata=None, **kwargs):
        """
        **kwargs 将会传递到 Table 的构造方法中。
        """
        self.metadata = metadata or MetaData()
        self.table_default_kw = kwargs
    
    def _get_table_default_kw(self):
        result = dict()
        for k in self.table_default_kw:
            result[k] = self.table_default_kw[k]
        return result

    def _build_table(self, tablename, items):
        """构建表对象"""
        indx_count = 0
        uniq_count = 0
        fkey_count = 0
        args = list()
        kwargs = self._get_table_default_kw()
        # 读取表的定义
        for item in items:
            if isinstance(item, dict):
                type_ = item["type"]
                if type_ == "index":
                    columns = item["columns"]
                    name = item['name']
                    if not name:
                        indx_count += 1
                        name = 'idx_%s_%d' % (tablename, indx_count)
                        #name = "idx_%s__%s" % (tablename, "__".join(columns))
                    item = Index(name, *columns)
                elif type_ == "unique":
                    columns = item["columns"]
                    name = item['name']
                    if not name:
                        uniq_count += 1
                        name = 'uniq_%s_%d' % (tablename, uniq_count)
                        #name = "uniq_%s__%s" % (tablename, "__".join(columns))
                    item = UniqueConstraint(*columns, name=name)
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

            @table('def')
            def table_def():
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
                return inner()
            return outter
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
    if PRIMARY in args:
        args.remove(PRIMARY)
        kwargs['primary_key'] = True
    return Column(*args, **kwargs)


def pkey(*args, **kwargs):
    """返回用于将多个列构建为主键的信息"""
    return PrimaryKeyConstraint(*args, **kwargs)


def fkey(*args, **kwargs):
    return ForeignKeyConstraint(*args, **kwargs)


def idx(*columns, **kwargs):
    """返回让 table 构建普通索引的信息"""
    name = kwargs.get('name', None)
    return {'type': 'index', 'columns': columns, 'name': name}


def uniq(*columns, **kwargs):
    """返回让 table 构建唯一索引的信息"""
    name = kwargs.get('name', None)
    return {'type': 'unique', 'columns': columns, 'name': name}

