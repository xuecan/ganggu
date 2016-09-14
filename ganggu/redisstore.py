# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
# Tools for Redis

Requirement:

* redis
"""

from urllib.parse import urlparse
import redis

RedisError = redis.RedisError

SOCKET_CONNECT_TIMEOUT = 2.0
SOCKET_TIMEOUT = 5.0


def make_redis_store(uri):
    """创建 Redis 客户端实例"""
    result = urlparse(uri)
    if result.scheme!='redis':
        raise ValueError('not a redis uri')
    host = result.hostname
    port = result.port
    database = int(result.path[1:])
    password = result.password or None
    store = redis.StrictRedis(
        host, port, database, password,
        socket_timeout=SOCKET_TIMEOUT, socket_connect_timeout=None
    )
    return store
