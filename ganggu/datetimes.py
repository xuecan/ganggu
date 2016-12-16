# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
一组与日期时间相关的工具
========================

本模块提供了以下便利的工具：

* 简单的关于时区的支持。
* 一些格式化日期时间的工具。
* 一些生成日期时间对象的工具。


时区
----

本模块提供了 ``UTC`` 对象用于表示协调世界时。提供了 ``get_system_timezone()``
方法用于获取系统当前使用的时区(该函数具有感知是否使用夏令时的能力)，以及
``get_default_timezone()`` 和 ``set_default_timezone()`` 函数用于获取和设置默认时区。

当本模块的函数处理的日期时间对象不包含时区信息时，会将它当做系统使用时区的时间。

而默认时区，是指本模块中与生成日期时间对象有关的函数默认使用的时区。本模块通常\
不会生成不含时区信息的日期时间对象。默认时区被默认的设置为 UTC+8。使用
``set_default_timezone()`` 函数可以修改默认时区。


关于时区的一些备忘
~~~~~~~~~~~~~~~~~~

在 Python 中，要获得最完整准确的关于时区的支持，需要使用 `pytz`_ 库。然而，大多数时候\
我们只需要一个明确的当前使用的时区，而不需要完整的时区知识。``pytz`` 提供给我们的\
太多，以至于有时候增加了处理的复杂程度。仅以中国使用的时间为例，我们通常不在意 1940
到 1941 年，以及 1986-1991 年以一些不同的规则启用了夏令时，也不在意 Asia/Shanghai
(上海)或 Asia/Urumqi (乌鲁木齐)的平均日出时间(Local Mean Time, LMT)有何不同。所以，\
我们并不需要一个压缩后仍有数百 KB 的库，仅用于日常处理当前时区的问题。

通常，我们只需要使用 Python 标准库中 ``datetime.timezone`` 类来创建时区即可。其构造方法\
接受可选的 ``name`` 参数作为时区的名称。目前，由于一些和日期时间有关的规范和惯例，要求\
表示日期时间的字符串使用时区缩写(如 RFC850 以及关于设置 Cookie 的规范)。换句话说就是使用
CST、EST 而不是 Asia/Shanghai、America/New_York 来表示时区。因此建议使用缩写作为时区的名称，\
方便使用日期时间格式 ``%Z`` 来生成符合规范的信息。

然而，程序员需要知道，时区缩写常常不具有唯一性，例如 CST 就可能用于表示：

* 中国标准时间(China Standard Time)，UTC +8
* (北美的)中部标准时间(Central Standard Time), UTC -6
* 古巴标准时间(Cuba Standard Time)，UTC -5

当然，当需要完整的时区支持时，`pytz`_ 仍是首选。而只需要简单的时区处理时，使用标准库的
``datetime.timezone`` 类并使用时区缩写就足够了。

.. _pytz: https://pypi.python.org/pypi/pytz/

**参考资料**

* `全球时区缩写一览 <https://www.timeanddate.com/time/zones/>`_ -
  由专注于日期和时间的组织提供的一份较为详细的速查清单。
* `PHP 语言支持的时区名称 <http://php.net/manual/en/timezones.php>`_ -
  这也是一份值得参考的清单。


日期时间的格式化
----------------

Python 标准库提供了格式化日期时间的处理，详情请参考 `datetime`_ 模块的相关文档。\
本模块提供了一些预设的函数，用于方便的将日期时间格式化为符合若干规范或使用场景\
所需的字符串。这些函数以 ``format_as_`` 开头。当传入这些函数的日期时间对象没有\
时区信息时，将会被认为是系统当前的时区的时间。

大多数格式化函数参考了 PHP 相关机制的设置，并且输出与 PHP 等价的机制是一样的，一个例外是对
ISO 8601 的处理，由于历史遗留问题，PHP 里声明为 ISO8601 的输出格式实际上并不符合该规范。

.. _datetime: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

"""


from datetime import datetime, timedelta, timezone, tzinfo
import time

__version__ = '1.0.0'

__all__ = [
    'get_system_timezone', 'with_system_timezone',
    'get_default_timezone', 'set_default_timezone', 'with_default_timezone',
    'format_as_atom', 'format_as_cookie', 'format_as_rss', 'format_as_w3c',
    'format_as_iso8601', 'format_as_rfc822', 'format_as_rfc850', 'format_as_rfc1036',
    'format_as_rfc1123', 'format_as_rfc2822', 'format_as_rfc3339',
    'now', 'before', 'after', 'UTC'
]


# UTC （协调世界时）时区
UTC = timezone(timedelta(seconds=0), 'UTC')


def get_system_timezone():
    """返回设备当前使用的时区信息。

    Returns:
        datetime.tzinfo: 设备当前使用的时区。
    """
    names = time.tzname
    if time.daylight:
        # 当前是夏令时
        seconds = time.altzone
        name = names[1]
    else:
        # 非夏令时
        seconds = time.timezone
        name = names[0]
    # time.timezone 以及 time.altzone 西半球是正数，和时区的规定正好相反
    seconds = - seconds
    return timezone(timedelta(seconds=seconds), name)


# 这个模块的一些用于生成日期时间的函数共用如下的默认时区设置。
_DEFAULT_TIMEZONE = timezone(timedelta(hours=8), 'CST')


def get_default_timezone():
    """返回默认时区。

    Returns:
        datetime.tzinfo: 使用本模块提供的函数时默认使用的时区。
    """
    return _DEFAULT_TIMEZONE


def set_default_timezone(tz):
    """设置默认的时区。

    Args:
        tz (datetime.tzinfo): 要设置的默认时区。
    """
    global _DEFAULT_TIMEZONE
    if not isinstance(tz, tzinfo):
        raise TypeError('first argument should be an instance of tzinfo')
    _DEFAULT_TIMEZONE = tz


def with_system_timezone(moment):
    """确保返回的日期时间以系统时区作为时区信息。

    Args:
        moment (datetime.datetime): 要处理的日期时间对象。

    Returns:
        datetime.datetime: 如果参数 ``moment`` 是所谓的 naive datetime，则\
                           附上系统时区。否则转换时区为系统时区。
    """
    tzinfo = get_system_timezone()
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=tzinfo)
    else:
        moment = moment.astimezone(tzinfo)
    return moment


def with_default_timezone(moment):
    """确保返回的日期时间以默认时区作为时区信息。

    Args:
        moment (datetime.datetime): 要处理的日期时间对象。

    Returns:
        datetime.datetime: 如果参数 ``moment`` 是所谓的 naive datetime，则\
                           附上默认时区。否则转换时区为默认时区。

    """
    tzinfo = get_default_timezone()
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=tzinfo)
    else:
        moment = moment.astimezone(tzinfo)
    return moment


def _prepare_formatter_args(moment, as_utc):
    """为 format_as_*() 函数提供参数处理。"""
    # 通常并不需要输出秒以下的部分
    moment = moment.replace(microsecond=0)
    # naive datetime? 附上系统时区
    if not moment.tzinfo:
        moment = with_system_timezone(moment)
    # 需要当做 UTC 输出吗？进行时区转换
    if as_utc:
        moment = moment.astimezone(UTC)
    return moment


def format_as_atom(moment, as_utc=False):
    """格式化为符合 ATOM 相关规范所需的时间格式。

    Args:
        moment (datetime.datetime): 要处理的日期时间。如果该参数是所谓的
                                    naive datetime，则附上系统时区。
        as_utc (bool): 是否转为 UTC 呈现。

    Returns:
        str: 符合 ATOM 相关规范所需的时间格式。
    """
    moment = _prepare_formatter_args(moment, as_utc)
    return moment.isoformat('T')


def format_as_iso8601(moment, as_utc=False):
    """格式化为符合 ISO 8601 规范的时间格式。

    当时区不是 UTC 时，与 ``format_as_atom()`` 的返回值一致。当时区是 UTC
    时，时区部分只输出一个字符 ``Z``。

    Args:
        moment (datetime.datetime): 要处理的日期时间。如果该参数是所谓的
                                    naive datetime，则附上系统时区。
        as_utc (bool): 是否转为 UTC 呈现。

    Returns:
        str: 符合 ISO 8601 规范所需的时间格式。
    """
    moment = _prepare_formatter_args(moment, as_utc)
    if moment.utcoffset() == timedelta(0):
        pattern = '%Y-%m-%dT%H:%M:%SZ'
        return moment.strftime(pattern)
    else:
        return moment.isoformat('T')


def format_as_cookie(moment, as_utc=False):
    """格式化为 Cookie 相关规范所需的时间格式。

    Args:
        moment (datetime.datetime): 要处理的日期时间。如果该参数是所谓的
                                    naive datetime，则附上系统时区。
        as_utc (bool): 是否转为 UTC 呈现。

    Returns:
        str: 符合 Cookie 相关规范所需的时间格式。
    """
    moment = _prepare_formatter_args(moment, as_utc)
    pattern = '%A, %d-%b-%Y %H:%M:%S %Z'
    return moment.strftime(pattern)


def format_as_rss(moment, as_utc=False):
    """格式化为 RSS 相关规范所需的时间格式。

    Args:
        moment (datetime.datetime): 要处理的日期时间。如果该参数是所谓的
                                    naive datetime，则附上系统时区。
        as_utc (bool): 是否转为 UTC 呈现。

    Returns:
        str: 符合 RSS 相关规范所需的时间格式。
    """
    moment = _prepare_formatter_args(moment, as_utc)
    pattern = '%a, %d %b %y %H:%M:%S %z'
    return moment.strftime(pattern)


def format_as_rfc850(moment, as_utc=False):
    """格式化为符合 RFC 850 规范所需的时间格式。

    Args:
        moment (datetime.datetime): 要处理的日期时间。如果该参数是所谓的
                                    naive datetime，则附上系统时区。
        as_utc (bool): 是否转为 UTC 呈现。

    Returns:
        str: 符合 RFC 850 规范所需的时间格式。
    """
    moment = _prepare_formatter_args(moment, as_utc)
    pattern = '%A, %d-%b-%y %H:%M:%S %Z'
    return moment.strftime(pattern)


def format_as_rfc822(*args, **kwrags):
    """Alias of ``format_as_rss()``."""
    return format_as_rss(*args, **kwrags)


def format_as_rfc1036(*args, **kwrags):
    """Alias of ``format_as_rss()``."""
    return format_as_rss(*args, **kwrags)


def format_as_rfc1123(*args, **kwrags):
    """Alias of ``format_as_rss()``."""
    return format_as_rss(*args, **kwrags)


def format_as_rfc2822(*args, **kwrags):
    """Alias of ``format_as_rss()``."""
    return format_as_rss(*args, **kwrags)


def format_as_rfc3339(*args, **kwrags):
    """Alias of ``format_as_atom()``."""
    return format_as_atom(*args, **kwrags)


def format_as_w3c(*args, **kwrags):
    """Alias of ``format_as_atom()``."""
    return format_as_atom(*args, **kwrags)


def now():
    """返回当前日期时间，使用默认时区。

    Returns:
        datetime.datetime: 当前的日期时间，使用默认时区。
    """
    return datetime.now(tz=get_system_timezone()).astimezone(get_default_timezone())


def after(seconds, moment=None):
    """返回基准时刻之后多少秒的时刻。

    Args:
        seconds (float): 秒。
        moment (datetime.datetime|None): 基准时刻，如果为 ``None``
                                         则使用当前时刻。

    Returns:
        datetime.datetime: 基准时刻之后多少秒的时刻。
    """
    moment = moment or now()
    return moment + timedelta(seconds=seconds)


def before(seconds, moment=None):
    """返回基准时刻之前多少秒的时刻。

    Args:
        seconds (float): 秒。
        moment (datetime.datetime|None): 基准时刻，如果为 ``None``
                                         则使用当前时刻。

    Returns:
        datetime.datetime: 基准时刻之前多少秒的时刻。
    """
    moment = moment or now()
    return moment - timedelta(seconds=seconds)
