# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
# Tools for Redis

Requirement:

* redis
"""

from urllib.parse import urlparse, unquote
import redis

RedisError = redis.RedisError

SOCKET_CONNECT_TIMEOUT = 2.0
SOCKET_TIMEOUT = 5.0


def make_redis_store(uri):
    """Create a redis instance.

    redis[+legacy|+strict]://[:password@]host:port/db
    """
    result = urlparse(uri)
    scheme = result.scheme.lower()
    if not result.scheme.startswith('redis'):
        raise ValueError('not a redis uri')
    host = result.hostname
    port = result.port
    database = int(result.path[1:])
    if result.password:
        password = unquote(result.password)
    else:
        password = None
    if scheme == 'redis+legacy':
        class_ = redis.Redis
    else:
        class_ = redis.StrictRedis
    store = class_(
        host, port, database, password,
        socket_timeout=SOCKET_TIMEOUT,
        socket_connect_timeout=SOCKET_CONNECT_TIMEOUT
    )
    return store
