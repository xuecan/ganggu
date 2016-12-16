# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
一些简单的数据结构
==================

本模块提供了几个简单的数据结构。
"""

__version__ = '1.0.0'


class Object(object):
    """简单对象。"""

    def __init__(self, **kwargs):
        for attr in kwargs:
            setattr(self, attr, kwargs[attr])


class Singleton(type):
    """用于实现 Singleton 设计模式的 metaclass

    需要运用 Singleton 设计模式的类，只需要该类或其祖先设置类属性 __metaclass__
    为本类即可：

        class A(object, metaclass=Singleton):
            pass

        class B(A):
            pass

    在上面的例子中，类 A 和 B 都是 singleton 的。
    """

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


class DictObject(dict):
    """类似字典，可以按属性存取"""

    def __init__(self, *args, **kwargs):
        super(DictObject, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
        else:
            self[name] = value

    def __delattr__(self, name):
        if name in self:
            self.pop(name)
        else:
            dict.__delattr__(self, name)


class Bindable:
    """将自身绑定到另一个对象上，这是一个 Mixin。"""

    def setup_bindable(self, bind_to, bind_at):
        """设置绑定属性名称。

        Args:
            bind_to (str): 本对象用于保存绑定目标的属性名。
            bind_at (str): 绑定目标用于保存本对象的属性名。
        """
        check = lambda x: x not in ['_bind_to', '_bind_at', '']
        bind_to = str(bind_to).strip()
        bind_at = str(bind_at).strip()
        if not check(bind_to) or not check(bind_at) or bind_to == bind_at:
            raise ValueError('invalid bind_to and/or bind_at argument(s)')
        self.__dict__['_bind_to'] = bind_to
        self.__dict__['_bind_at'] = bind_at
        self.__dict__[bind_to] = None

    def bind(self, to_):
        """将本对象绑定到目标对象上。

        Args:
            to_ (object): 绑定目标。
        """
        bind_to = self.__dict__['_bind_to']
        if self.__dict__[bind_to]:
            raise RuntimeError('this object already has a binding object')
        self.__dict__[bind_to] = to_
        setattr(to_, self.__dict__['_bind_at'], self)

    def unbind(self):
        """解除本对象与目标对象的绑定。"""
        bind_to = self.__dict__['_bind_to']
        to_ = self.__dict__[bind_to]
        if to_:
            delattr(to_, self.__dict__['_bind_at'])
            self.__dict__[bind_to] = None
