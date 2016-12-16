# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

from ganggu.datastructures import *
import pytest


def test_object():
    obj1 = Object(a=1, b=2)
    assert obj1.a == 1 and obj1.b == 2, 'something wrong in Object'


class Lib(Bindable, object, metaclass=Singleton):
    pass


class App(Lib):
    pass


def test_singleton():
    lib1 = Lib()
    lib2 = Lib()
    app1 = App()
    app2 = App()
    assert lib1 is lib2, 'Lib is not Singleton'
    assert app1 is app2, 'App is not Singleton'
    assert lib1 is not app1, 'Lib is App'


def test_dictobj():
    obj = DictObject(dict(a=1))
    assert obj.a == obj['a']
    assert obj.a == 1


def test_bindable():
    app = App()
    lib = Lib()
    with pytest.raises(ValueError):
        lib.setup_bindable('', '')
    with pytest.raises(ValueError):
        lib.setup_bindable('_bind_to', '_bind_at')
    lib.setup_bindable('app', 'lib')
    lib.bind(app)
    assert lib.app is app and app.lib is lib, 'something wrong in bind()'
    with pytest.raises(RuntimeError):
        lib.bind(app)
    lib.unbind()
    assert lib.app is None and not hasattr(app, 'lib'), 'something wrong in unbind()'
