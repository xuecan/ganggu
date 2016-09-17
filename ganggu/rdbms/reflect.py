# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
# 数据库反射机制

这是一个实验性的模块，用于从现有的关系数据库中生成可以在程序中直接使用的 Table 等定义组件。

http://docs.sqlalchemy.org/en/latest/core/reflection.html#fine-grained-reflection-with-inspector
"""

from collections import OrderedDict
from keyword import iskeyword
from textwrap import dedent
from copy import deepcopy
from sqlalchemy import inspect


class ReflectedTable(object):

    def __init__(self, name):
        self.name = name
        self.columns = OrderedDict()
        self.pkeys = None
        self.uniqs = list()
        self.idxes = list()
        self.fkeys = list()
        self.fkeyset = set()

    def set_cols(self, columns):
        for column in columns:
            name = column.pop('name')
            type_ = column.pop('type')
            args = [name, type_]
            kwargs = deepcopy(column)
            self.columns[name] = {'args': args, 'kwargs': kwargs}

    def set_pkeys(self, pkeys):
        column_names = pkeys['constrained_columns']
        if pkeys['name']:
            self.pkeys = {
                'args': column_names,
                'kwargs': {'name': pkeys['name']},
            }
        else:
            for name in column_names:
                self.columns[name]['kwargs']['primary_key'] = True

    def set_idxes(self, indexes):
        for item in indexes:
            data = {
                'args': item['column_names'],
                'kwargs': {'name': item['name']},
            }
            if item['unique']:
                self.uniqs.append(data)
            else:
                self.idxes.append(data)

    def set_fkeys(self, fkeys):
        for fkey in fkeys:
            name = fkey['name']
            kwargs = fkey['options']
            cols = fkey['constrained_columns']
            cols_tuple = tuple(cols)
            self.fkeyset.add(cols_tuple)
            schema = fkey['referred_schema']
            table = fkey['referred_table']
            prefix = table + '.'
            if schema:
                prefix = schema + '.' + prefix
            refcols = list(map(lambda x: prefix + x, fkey['referred_columns']))
            if len(cols) == 1:
                self.columns[cols[0]]['kwargs']['fkey'] = {'args': refcols, 'kwargs': kwargs}
            else:
                data = {
                    'args': [cols, refcols, name],
                    'kwargs': kwargs,
                }
                self.fkeys.append(data)


def _repr_type(type_):
    result = repr(type_)
    #result = result.replace('(display_width=', '(')
    #result = result.replace('(length=', '(')
    return result


def _flatten_col(mapping):
    result = list()
    for key in mapping:
        value = mapping[key]
        if key == 'default':
            if value is None:
                # 忽略 default=None
                pass
            elif isinstance(value, str):
                if value.startswith("'") and value.endswith("'"):
                    result.append('server_default=%s' % value)
                else:
                    result.append('server_default=text(%s)' % repr(value))
            else:
                result.append('%s=%s' % (key, repr(value)))
        elif key == 'autoincrement' and value is False:
            # 忽略 autoincrement=False
            pass
        elif key == 'nullable' and value is True:
            # 忽略 nullable=True
            pass
        else:
            result.append('%s=%s' % (key, repr(value)))
    return result


def _flatten(mapping):
    result = list()
    for key in mapping:
        value = mapping[key]
        result.append('%s=%s' % (key, repr(value)))
    return result


def _render_call(funcname, data):
    buf = funcname + '('
    buf += ', '.join(map(lambda x: repr(x), data['args']))
    if data['kwargs']:
        buf += ', '
        buf += ', '.join(_flatten(data['kwargs']))
    buf += ')'
    return buf


class Renderer(object):

    def __init__(self, reflected):
        self.reflected = reflected

    def render(self):
        buf = self._render_start()
        for column_name in self.reflected.columns:
            buf += self._render_column(self.reflected.columns[column_name])
        buf += self._render_primary_key()
        buf += self._render_unique_indexes()
        buf += self._render_indexes()
        buf += self._render_foreign_keys()
        buf += self._render_end()
        return buf

    def __str__(self):
        return self.render()


class StandardRenderer(Renderer):

    def _render_start(self):
        tpl_common = "%s = Table('%s', metadata"
        tpl_keyword = "%s_ = Table('%s', metadata"
        name = self.reflected.name
        tpl = tpl_keyword if iskeyword(name) else tpl_common
        return tpl_common % (name, name)

    def _render_end(self):
        return '\n)\n\n\n'

    def _render_column(self, column):
        col = deepcopy(column)
        args = col['args']
        name = args[0]
        type_ = _repr_type(args[1])
        kwargs = col['kwargs']
        primary_key = kwargs.pop('primary_key', None)
        fkey = kwargs.pop('fkey', None)
        nullable = kwargs.pop('nullable', True)
        buf = ',\n' + ' ' * 4
        buf += 'Column('
        buf += repr(name) + ', ' + type_
        if primary_key:
            buf += ', primary_key=True'
        if fkey:
            buf += ', ' + _render_call('ForeignKey', fkey)
        if not nullable:
            buf += ', nullable=False'
        rest = ', '.join(_flatten_col(kwargs))
        if rest:
            buf += ', ' + rest
        buf += ')'
        return buf

    def _render_primary_key(self):
        buf = ''
        pkeys = self.reflected.pkeys
        if pkeys:
            buf = ',\n' + ' ' * 4
            buf += _render_call('PrimaryKeyConstraint', pkeys)
        return buf

    def _render_unique_indexes(self):
        buf = ''
        for item in self.reflected.uniqs:
            buf += ',\n' + ' ' * 4
            buf += _render_call('UniqueConstraint', item)
        return buf

    def _render_indexes(self):
        buf = ''
        for item in self.reflected.idxes:
            cols_tuple = tuple(item['args'])
            if cols_tuple not in self.reflected.fkeyset:
                data = deepcopy(item)
                name = data['kwargs'].pop('name')
                data['args'].insert(0, name)
                buf += ',\n' + ' ' * 4
                buf += _render_call('Index', data)
        return buf

    def _render_foreign_keys(self):
        buf = ''
        for item in self.reflected.fkeys:
            buf += ',\n' + ' ' * 4
            buf += _render_call('ForeignKeyConstraint', item)
        return buf


class ShortcutRenderer(Renderer):

    def _render_start(self):
        tpl_common = dedent('''\
            @schema.table
            def %s():
                return [
            ''')
        tpl_keyword = dedent('''\
            @schema.table('%s')
            def table_%s():
                return [
            ''')
        name = self.reflected.name
        if iskeyword(name):
            return tpl_keyword % (name, name)
        else:
            return tpl_common % name

    def _render_end(self):
        return '    ]\n\n\n'

    def _render_column(self, column):
        col = deepcopy(column)
        args = col['args']
        name = args[0]
        type_ = _repr_type(args[1])
        kwargs = col['kwargs']
        primary_key = kwargs.pop('primary_key', None)
        fkey = kwargs.pop('fkey', None)
        nullable = kwargs.pop('nullable', True)
        buf = ' ' * 8
        buf += 'col('
        buf += repr(name) + ', ' + type_
        if primary_key:
            buf += ', PRIMARY'
        if fkey:
            buf += ', ' + _render_call('FOREIGN', fkey)
        if not nullable:
            buf += ', NOTNULL'
        rest = ', '.join(_flatten_col(kwargs))
        if rest:
            buf += ', ' + rest
        buf += '),\n'
        return buf

    def _render_primary_key(self):
        buf = ''
        pkeys = self.reflected.pkeys
        if pkeys:
            buf = '        '
            buf += _render_call('pkeys', pkeys)
            buf += ',\n'
        return buf

    def _render_unique_indexes(self):
        buf = ''
        for item in self.reflected.uniqs:
            buf += '        '
            buf += _render_call('uniq', item)
            buf += ',\n'
        return buf

    def _render_indexes(self):
        buf = ''
        for item in self.reflected.idxes:
            cols_tuple = tuple(item['args'][:])
            if cols_tuple not in self.reflected.fkeyset:
                data = deepcopy(item)
                name = data['kwargs'].pop('name')
                data['args'].insert(0, name)
                buf += '        '
                buf += _render_call('idx', data)
                buf += ',\n'
        return buf

    def _render_foreign_keys(self):
        buf = ''
        for item in self.reflected.fkeys:
            buf += '        '
            buf += _render_call('fkeys', item)
            buf += ',\n'
        return buf


class Reflector(object):

    def __init__(self, engine):
        self.engine = engine
        self.inspector = inspect(engine)

    def tables(self, schema=None):
        result = list()
        items = self.inspector.get_sorted_table_and_fkc_names(schema)
        for item in items:
            if item[0]:
                result.append(item[0])
        return result

    def render(self, tablename=None):
        if not tablename:
            result = ''
            for tablename in self.tables():
                result += self.render(tablename)
            return result
        else:
            reflected = ReflectedTable(tablename)
            reflected.set_cols(self.inspector.get_columns(tablename))
            reflected.set_pkeys(self.inspector.get_pk_constraint(tablename))
            reflected.set_idxes(self.inspector.get_indexes(tablename))
            reflected.set_fkeys(self.inspector.get_foreign_keys(tablename))
            renderer = ShortcutRenderer(reflected)
            return renderer.render()
