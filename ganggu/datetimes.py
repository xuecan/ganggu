# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
# 一些与时间相关的实用函数

依赖：

  * [python-dateutil](https://dateutil.readthedocs.io/en/stable/)
"""


from datetime import datetime, timedelta
import time
from dateutil.tz import tzutc
from dateutil.parser import parse as parse_datetime


# 协调世界时
UTC = tzutc()


def format_datetime(moment, as_utc=False):
    """生成符合 ISO 8601 规范的日期时间字符串

    如果 as_utc 为 False，使用业务默认时区"""
    pattern = "%Y-%m-%dT%H:%M:%S"
    if as_utc:
        moment = moment.astimezone(UTC)
        pattern += "Z"
    else:
        moment = moment.astimezone(TZ_DEFAULT)
        pattern += "%z"
    return moment.strftime(pattern)


def now():
    """返回当前日期时间，使用业务默认时区"""
    return datetime.now(tz=TZ_LOCAL).astimezone(TZ_DEFAULT)


def after(seconds):
    return now() + timedelta(seconds=seconds)


# --------------------------------------------------------------
# 补丁
# --------------------------------------------------------------

from dateutil.tz import tzoffset


def tzoffset____init__(self, name, offset):
    """dateutil.tz.tzoffset 补丁

    应用该补丁后，处理 ISO 8601 的时间格式得到的时区对象名称形如 "+08:00" 而非 None
    在 strftime 中使用 "%z" 可以得到 "+0800"，"%Z" 可以得到 "+08:00"
    """
    if name is None:
        hours = int(offset / 3600)
        minutes = int((offset - hours * 3600) / 60)
        name = '%+03d:%02d' % (hours, minutes)
    self._name = name
    self._offset = timedelta(seconds=offset)


# 应用补丁
tzoffset.__init__ = tzoffset____init__


# --------------------------------------------------------------
# 以下“常量”需要打过补丁后设置

# 运行程序的计算机系统上设置的时区
TZ_LOCAL = tzoffset(None, -time.timezone)  # time.timezone 西半球是正数

# 本系统业务上默认使用的时区
TZ_DEFAULT = tzoffset(None, 8 * 3600)      # UTC+8(北京/台北/新加坡等)
