# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
# 数据库连接装置

这个模块提供了 Facility 类，用于关联 SQLAlchemy 的数据库引擎对象 Engine 和数据库会话
Session 对象。
"""

from sqlalchemy.orm import sessionmaker, scoped_session


class Facility(object):

    def __init__(self, engine=None):
        self._engine = None
        self._sessionmaker = sessionmaker()
        self._session = scoped_session(self._sessionmaker)
        if engine:
            self.bind(engine)

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        if not self.engine:
            raise RuntimeError('engine not bound')
        return self._session

    @property
    def connection(self):
        return self.session.connection()

    def bind(self, engine):
        if self._engine:
            raise RuntimeError('engine has been bound')
        self._engine = engine
        self._sessionmaker.configure(bind=engine)

    def remove_session(self, exception=None):
        """Dispose of the current Session, if present.

        http://docs.sqlalchemy.org/en/rel_0_9/orm/contextual.html#sqlalchemy.orm.scoping.scoped_session.remove

        这是一个 teardown_request:
        http://flask.pocoo.org/docs/0.10/reqcontext/#teardown-callbacks
        """
        if self.engine:
            self.session.remove()


class Facilities(object):

    def __init__(self):
        self._names = set()

    def __setattr__(self, name, value):
        if isinstance(value, Facility):
            self._names.add(name)
        object.__setattr__(self, name, value)

    def get_all(self):
        data = dict()
        for name in self._names:
            facility = getattr(self, name)
            data[name] = facility
        return data

    def remove_sessions(self, exception=None):
        """Dispose of the current Session, if present.

        http://docs.sqlalchemy.org/en/rel_0_9/orm/contextual.html#sqlalchemy.orm.scoping.scoped_session.remove

        这是一个 teardown_request:
        http://flask.pocoo.org/docs/0.10/reqcontext/#teardown-callbacks
        """
        for name in self._names:
            facility = getattr(self, name)
            facility.remove_session()
