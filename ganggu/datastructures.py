# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license


class Object(object):
    """简单对象"""

    def __init__(self, **kwargs):
        for attr in kwargs:
            if attr not in self.__dict__:
                setattr(self, attr, kwargs[attr])
            else:
                raise KeyError('invalid attribute name "%s"' % attr)


class singleton(type):
    """用于实现 singleton 设计模式的 metaclass

    需要运用 singleton 设计模式的类，只需要该类或其祖先设置类属性 __metaclass__
    为本类即可：

        class A(object):
            __metaclass__ = singleton

        class B(A):
            pass

    在上面的例子中，类 A 和 B 都是 singleton 的。
    """

    def __init__(cls, name, bases, dict):
        super(singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance = super(singleton, cls).__call__(*args, **kw)
        return cls.instance


class DictObject(dict):
    """类似字典，可以按属性存取"""

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

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


class Boundable:
    """将自身绑定到另一个对象上"""

    def _setup_boundable(self, bind_to, bind_at):
        self.__dict__['_bind_to'] = bind_to
        self.__dict__['_bind_at'] = bind_at
        self.__dict__[bind_to] = None

    def bind(self, to_):
        setattr(self, self._bind_to, to_)
        setattr(to_, self._bind_at, self)

    def unbind(self):
        to_ = getattr(self, self._bind_to)
        if to_:
            delattr(to_, self._bind_at)
            setattr(self, self._bind_to, None)
