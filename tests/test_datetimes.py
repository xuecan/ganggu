# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license


from datetime import datetime, timedelta, tzinfo, timezone
import time
from ganggu.datetimes import *


# 本程序认为连续两次获取时间的操作，获得的时间不应该超过 0.5 秒
# (除非有类似 ntpdate 这样的程序恰好在此刻修正了时间)
_INTERVAL = 0.5


def test_utc():
    assert UTC == timezone.utc, 'UTC 对象看起来不正确'
    assert UTC.tzname(None) == 'UTC', 'UTC 的时区名应为 UTC'


def test_system_timezone():
    tz = get_system_timezone()
    assert isinstance(tz, tzinfo), '系统时区应该是 datetime.tzinfo 的实例'
    assert tz.tzname(None) in time.tzname, '看起来系统时区的名称并不正确'
    offset0 = tz.utcoffset(None)
    now_sys = datetime.now()
    now_utc = datetime.utcnow()
    offset1 = now_sys - now_utc
    assert abs((offset0 - offset1).total_seconds()) < _INTERVAL, \
        '看起来系统时区的偏移值不太正确'


def test_default_timezone():
    tz = get_default_timezone()
    assert isinstance(tz, tzinfo), '默认时区应该是 datetime.tzinfo 的实例'
    assert isinstance(tz.tzname(None), str), '默认时区应该有名称'


def test_with_system_timezone():
    now0 = with_system_timezone(datetime.now())
    now1 = datetime.now(timezone.utc)
    now2 = with_system_timezone(now1)
    assert now0.tzinfo == get_system_timezone(), \
        'with_system_timezone() 返回值应该使用系统时区'
    assert now2.tzinfo == get_system_timezone(), \
        'with_system_timezone() 返回值应该使用系统时区'
    assert abs((now1 - now0).total_seconds()) < _INTERVAL, \
        'with_system_timezone() 似乎有问题'
    assert now2 == now1, 'with_system_timezone() 似乎有问题'


def test_with_default_timezone():
    now0 = with_default_timezone(datetime.now())
    now1 = with_default_timezone(datetime.utcnow())
    now2 = with_default_timezone(datetime.now(timezone.utc))
    offset0 = get_default_timezone().utcoffset(None)
    offset1 = now0 - now1
    assert now0.tzinfo == get_system_timezone(), \
        'with_default_timezone() 返回值应该使用默认时区'
    assert now2.tzinfo == get_system_timezone(), \
        'with_default_timezone() 返回值应该使用默认时区'
    assert abs((offset1 - offset0).total_seconds()) < _INTERVAL, \
        'with_default_timezone() 似乎有问题'


def test_format():
    moment = now()
    if moment.tzinfo == timezone.utc:
        moment.astimezone(timezone(timedelta(hours=8), 'CST'))
    moment = moment.replace(microsecond=0)
    # +HH:MM 的时区形式
    tz_suffix = moment.strftime('%z')
    tz_suffix = tz_suffix[:3] + ':' + tz_suffix[-2:]
    # ATOM 和 ISO 8601 格式的日期时间检查
    pattern = '%Y-%m-%dT%H:%M:%S' + tz_suffix
    text = format_as_atom(moment)
    assert text == format_as_iso8601(moment), \
        'something wrong in format_as_atom() or format_as_iso8601()'
    check = datetime.strptime(text, pattern)
    check = check.replace(tzinfo=moment.tzinfo)  # 这种情况 strptime 生成的是 naive datetime
    assert check == moment, 'something wrong in format_as_atom()'
    pattern = '%Y-%m-%dT%H:%M:%S+00:00'
    text = format_as_atom(moment, True)
    check = datetime.strptime(text, pattern)
    check = check.replace(tzinfo=UTC)  # 这种情况 strptime 生成的是 naive datetime
    assert check == moment, 'something wrong in format_as_atom()'
    # Cookie 格式的日期时间检查
    pattern = '%A, %d-%b-%Y %H:%M:%S %Z'
    text = format_as_cookie(moment)
    check = datetime.strptime(text, pattern)
    check = check.replace(tzinfo=moment.tzinfo)  # 这种情况 strptime 生成的是 naive datetime
    assert check == moment, 'something wrong in format_as_cookie()'
    text = format_as_cookie(moment, True)
    check = datetime.strptime(text, pattern)
    check = check.replace(tzinfo=UTC)  # 这种情况 strptime 生成的是 naive datetime
    assert check == moment, 'something wrong in format_as_cookie()'
    # RSS 格式的日期时间检查
    pattern = '%a, %d %b %y %H:%M:%S %z'
    text = format_as_rss(moment)
    check = datetime.strptime(text, pattern)
    assert check == moment, 'something wrong in format_as_rss()'
    text = format_as_rss(moment, True)
    check = datetime.strptime(text, pattern)
    assert check == moment, 'something wrong in format_as_rss()'
    # RFC 850 格式的日期时间检查
    pattern = '%A, %d-%b-%y %H:%M:%S %Z'
    text = format_as_rfc850(moment)
    check = datetime.strptime(text, pattern)
    check = check.replace(tzinfo=moment.tzinfo)  # 这种情况 strptime 生成的是 naive datetime
    assert check == moment, 'something wrong in format_as_rfc850()'
    text = format_as_rfc850(moment, True)
    check = datetime.strptime(text, pattern)
    check = check.replace(tzinfo=UTC)  # 这种情况 strptime 生成的是 naive datetime
    assert check == moment, 'something wrong in format_as_rfc850()'
    # ISO 8601 特殊格式的检查
    pattern = '%Y-%m-%dT%H:%M:%SZ'
    text = format_as_iso8601(moment, True)
    check = datetime.strptime(text, pattern)
    check = check.replace(tzinfo=UTC)  # 这种情况 strptime 生成的是 naive datetime
    assert check == moment, 'something wrong in format_as_iso8601()'


def test_now():
    now0 = now()
    # Python 标准库文档提供的例子
    now1 = datetime.now(timezone.utc)
    assert (now1 - now0).total_seconds() < _INTERVAL, 'now() 似乎有问题'
    assert now0.tzinfo == get_default_timezone(), \
        'now() 的返回值应该携带默认时区信息'


def test_before_after():
    now0 = now()
    moment1 = before(3600, now0)
    moment2 = after(3600, now0)
    assert moment2 - moment1 == timedelta(seconds=7200), \
        'before() 或 after() 存在问题'
