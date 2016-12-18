# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
一个缓存域名解释的机制
======================

默认的，Python 或者 requests 处理 URL 时，并不会缓存域名解释的结果。\
这个模块提供了一个简单的机制来解决这个问题。

函数 ``hostname_to_ipaddr()`` 用于获取指定主机对应的 IPv4 的地址，\
这个过程会缓存结果以便在缓存过期之前都可以使用。

更进一步，函数 ``url()`` 会转换指定 URL 的 hostname 部分返回使用
IPv4 地址形式的 URL。许多时候，我们希望在实际发起请求时才去做这样的转换，
``smart_url()`` 可以返回一个 callable，在需要的时候才去执行转换操作。

开发人员可以自行设定缓存机制，它应该是 ``werkzeug.contrib.cache.BaseCache``
子类的实例。默认的这个模块使用 ``werkzeug.contrib.cache.SimpleCache``。

本模块依赖如下第三方库：

* `Werkzeug <http://werkzeug.pocoo.org/>`_。
"""

import socket
from urllib.parse import urlparse, urlunparse
from functools import partial
from werkzeug.contrib.cache import BaseCache, SimpleCache

__version__ = '1.0.0'


# 运行时的缓存机制实例
RUNTIME = {
    'CACHE': None
}


def set_cache_system(cache=None):
    """设置缓存机制实例。

    Args:
        cache (werkzeug.contrib.cache.BaseCache): 缓存系统。
    """
    if not isinstance(cache, BaseCache):
        raise TypeError('first argument should be an instance of'
                        ' werkzeug.contrib.cache.BaseCache or None')
    RUNTIME['CACHE'] = cache


# 设置默认的缓存机制实例
set_cache_system(SimpleCache(default_timeout=3600))


def hostname_to_ipaddr(hostname, timeout=None):
    """返回 hostname 对应的 IPv4 的地址。结果将被缓存。

    Args:
        hostname (str): 主机名称。
        timeout (int|None): 如果为 None 则缓存本模块默认配置的时间。否则缓存
                            指定的秒数。特别的，如果为 0 表示缓存不过期。

    Returns:
        str: IPv4 地址的字符串形式。
    """
    hostname = str(hostname).strip()
    key = 'resolve:'+hostname
    cache = RUNTIME['CACHE']
    ipaddr = cache.get(key)
    if ipaddr is not None:
        return ipaddr
    result = socket.getaddrinfo(hostname, 0, socket.AF_INET, socket.SOCK_STREAM)
    if not result:
        raise RuntimeError('cannot getaddrinfo for %s' % hostname)
    ipaddr = result[0][-1][0]
    cache.set(key, ipaddr, timeout)
    return ipaddr


def url(url_):
    """替换 URL 中 hostname 部分为 IPv4 地址。

    Args:
        url_ (str): URL。

    Returns:
        str: URL。
    """
    parsed = urlparse(url_)
    if not parsed.hostname:
        raise ValueError('not hostname in the url')
    ipaddr = hostname_to_ipaddr(parsed.hostname)
    netloc = ''
    if parsed.username:
        netloc += parsed.username
    if parsed.password:
        netloc += ':' + parsed.password
    if parsed.username or parsed.password:
        netloc += '@'
    netloc += ipaddr
    if parsed.port:
        netloc += ':' + str(parsed.port)
    return urlunparse((parsed.scheme, netloc, parsed.path,
                       parsed.params, parsed.query, parsed.fragment))


def smart_url(url_):
    """返回延时执行 ``url()`` 函数的函数。

    Args:
        url_: 要延时处理的 URL。

    Returns:
        callable: 执行这个 callable 将会调用 ``url(url_)``。
    """
    return partial(url, url_)
