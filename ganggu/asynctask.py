# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
Celery 应用程序生成器

Celery 应用程序的配置众多，这里提供一个快速的生成器，避免经常需要查阅手册。

本模块根据 Celery 4.0.0rc4 重新编写。配置详情请参考：

* http://docs.celeryproject.org/en/master/userguide/configuration.html
"""

import celery
if '4.0.0' > celery.__version__:
    raise RuntimeError('Require celery 4.0.0rc4 or up')

from celery import Celery
from kombu.exceptions import OperationalError
from .datastructures import Object


def make_worker(name, set_as_current=True):
    """返回默认的 worker 实例，还需要进一步配置方可使用"""
    name = str(name)
    worker = Celery(name, set_as_current=set_as_current)
    worker.conf.update(
        # names
        task_default_queue=name,
        task_default_exchange=name,
        task_default_routing_key=name,
        # genenals
        accept_content=['json'],
        enable_utc=True,
        timezone='Asia/Shanghai',
        # tasks
        task_serializer='json',
        task_compression=None,
        task_protocol=2,
        task_track_started=True,
        task_publish_retry=False,         # no retry
        # results
        result_serializer='json',
        result_compression=None,
        result_expires=3600,              # 1 hour
        # workers
        worker_prefetch_multiplier=1,     # no prefetch
        worker_disable_rate_limits=True,  # no rate limit
        worker_max_tasks_per_child=1000,  # prevent memory leak
        worker_hijack_root_logger=False   # we have logkit
    )
    return worker


def with_retries(worker, max_=3, start=0, interval=0.2):
    worker.conf.update(
        task_publish_retry=True,
        task_publish_retry_policy={
            'max_retries': max_,
            'interval_start': start,
            'interval_step': interval,
            'interval_max': interval,
        }
    )


def _with_broker(worker, broker, read_broker=None):
    if read_broker:
        worker.conf.broker_write_url = broker
        worker.conf.broker_read_url = read_broker
    else:
        worker.conf.broker_url = broker


def with_amqp_broker(worker, broker, read_broker=None):
    worker.conf.task_queue_ha_policy = 'all'
    _with_broker(worker, broker, read_broker)


def with_redis_broker(worker, broker, read_broker=None):
    worker.conf.broker_transport_options = {
        'visibility_timeout': 3600,
        'fanout_prefix': True,
        'fanout_patterns': True,
    }
    _with_broker(worker, broker, read_broker)


def with_backend(worker, backend):
    worker.conf.result_backend = backend


# patch: don't use image
import celery.utils.term
celery.utils.term.supports_images = lambda: False
