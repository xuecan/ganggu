# -*- coding: UTF-8 -*-
# Copyright (C) 2012-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
日志工具
========

加载本模块后，将会使用这里定义的 ``Logger`` 类扩展 Python 标准库 ``logging``
的日志器类。同时，支持了比 Python 标准库更多的日志等级，如下表：

+-----------+-------+-----------------------------------+
| Level     | Value | Defined                           |
+-----------+-------+-----------------------------------+
| NOTHING   |  9999 | n/a                               |
| EMERGENCY |    70 | RFC 5424                          |
| ALERT     |    60 | RFC 5424                          |
| CRITICAL  |    50 | RFC 5424, Python Standard Library |
| ERROR     |    40 | RFC 5424, Python Standard Library |
| WARNING   |    30 | RFC 5424, Python Standard Library |
| NOTICE    |    25 | RFC 5424                          |
| INFO      |    20 | RFC 5424, Python Standard Library |
| VERBOSE   |    15 | verboselogs 1.0                   |
| DEBUG     |    10 | RFC 5424, Python Standard Library |
| SPAM      |     5 | verboselogs 1.1                   |
| NOTSET    |     0 | Python Standard Library           |
+-----------+-------+-----------------------------------+

开发人员可以使用本模块定义的 ``get_logger()`` 函数代替 ``logging.getLogger()``
来获取日志器对象。

本模块提供了一系列 ``setup_*_handler()`` 函数用于快速设置日志处理器。

本模块依赖如下第三方库：

* `coloredlogs <https://coloredlogs.readthedocs.io/en/latest/>`_。
"""

import logging
from logging import getLogger
from logging import StreamHandler
from logging.handlers import WatchedFileHandler
from coloredlogs import ColoredFormatter

__version__ = '1.1.0'


# 一些默认值
DEFAULTS = {
    # 默认的日志格式，使用了多线程或协程技术的程序可能需要修改这个格式
    'LOG-FORMAT': '%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s',
    # 日期格式，年份只用两个字符，在日志中这通常不会引起歧义
    'DATE-FORMAT': '%y-%m-%d %H:%M:%S',
    # 彩色终端输出使用的字段样式
    'FIELD-STYLES': {
        'hostname':    {'color': 'magenta'},
        'programname': {'color': 'blue'},
        'name':        {'color': 'cyan'},
        'levelname':   {'color': 'black', 'bold': True},
        'asctime':     {'color': 'green'},
    },
    # 彩色终端输出使用的等级样式
    'LEVEL-STYLES': {
        'emergency': {'color': 'red', 'bold': True},
        'alert':     {'color': 'red', 'bold': True},
        'critical':  {'color': 'red', 'bold': True},
        'error':     {'color': 'red'},
        'warning':   {'color': 'yellow'},
        'info':      {'color': 'cyan'},
        'verbose':   {},
        'debug':     {'color': 'green'},
        'spam':      {'color': 'blue'}
    },
}


# 在 DEBUG 和 INFO 之间增加 SPAM 级别(兼容 verboselogs 1.1)
logging.addLevelName(5, 'SPAM')
logging.SPAM = 5

# 在 INFO 和 DEBUG 之间增加 VERBOSE 级别(兼容 verboselogs 1.0)
logging.addLevelName(15, 'VERBOSE')
logging.VERBOSE = 15

# 在 WARNING 和 INFO 之间增加 NOTICE 级别(兼容 RFC 5424)
logging.addLevelName(25, 'NOTICE')
logging.NOTICE = 25

# 增加 ALERT 级别(兼容 RFC 5424)
logging.addLevelName(60, 'ALERT')
logging.ALERT = 60

# 增加 EMERGENCY 级别(兼容 RFC 5424)
logging.addLevelName(70, 'EMERGENCY')
logging.EMERGENCY = 70

# 一个特殊的实际上不显示日志的等级
logging.addLevelName(9999, 'NOTHING')
logging.NOTHING = 9999


class Logger(logging.Logger):
    """用于替换 Python 标准库 Logger 类的日志器。"""

    def __init__(self, *args, **kwargs):
        super(Logger, self).__init__(*args, **kwargs)

    def spam(self, *args, **kwargs):
        self.log(logging.SPAM, *args, **kwargs)

    def verbose(self, *args, **kwargs):
        self.log(logging.VERBOSE, *args, **kwargs)

    def notice(self, *args, **kwargs):
        self.log(logging.NOTICE, *args, **kwargs)

    def alert(self, *args, **kwargs):
        self.log(logging.ALERT, *args, **kwargs)

    def emergency(self, *args, **kwargs):
        self.log(logging.EMERGENCY, *args, **kwargs)

    def nothing(self, *args, **kwargs):
        self.log(logging.NOTHING, *args, **kwargs)

    def setLevel(self, level):
        """设置日志等级，返回实例自身。

        Args:
            level (str|int): 日志等级。

        Returns:
            self: 实例自身。
        """
        super(Logger, self).setLevel(level)
        return self

    def set_propagate(self, propagate):
        """设置 propagate 属性并返回实例自身。

        Args:
            propagate (bool): 日志消息是否向上传播。

        Returns:
            self: 实例自身。
        """
        self.propagate = bool(propagate)
        return self

    def addHandler(self, hdlr):
        """添加日志处理器，返回实例自身。

        Args:
            hdlr (logging.Handler): 日志处理器。

        Returns:
            self: 实例自身。
        """
        super(Logger, self).addHandler(hdlr)
        return self

    def removeHandler(self, hdlr):
        """移除日志处理器，返回实例自身。

        Args:
            hdlr (logging.Handler): 日志处理器。

        Returns:
            self: 实例自身。
        """
        super(Logger, self).removeHandler(hdlr)
        return self

    def clear_handlers(self):
        """清空日志处理器，返回实例自身。

        Returns:
            self: 实例自身。
        """
        for hdlr in self.handlers[:]:
            self.removeHandler(hdlr)
        return self

    # 通过别名的方式实现这个类的命名惯例
    setPropagate = set_propagate
    clearHandlers = clear_handlers


class RootLogger(Logger):
    """用于替代 ``logging.RootLogger`` 的类。

    A root logger is not that different to any other logger, except that
    it must have a logging level and there is only one instance of it in
    the hierarchy.
    """

    def __init__(self, level):
        """Initialize the logger with the name "root"."""
        super(RootLogger, self).__init__('root', level)


# 设置 logging 模块使用这里定义的 Logger 类作为日志器类。
logging.setLoggerClass(Logger)


# 一些针对 root 的 Hack，在 ``logging`` 中对应的这几个属性是直接写在模块中的。
# 这些 Hack 确保了使用 ``get_logger()`` 或 ``logging.getLogger()``
# 都能得到本模块定义的 ``Logger`` 类的实例。
logging.RootLogger = RootLogger
logging.root = RootLogger(logging.WARNING)
Logger.root = logging.root
Logger.manager = logging.Manager(Logger.root)


def get_logger(name=None):
    """Return a logger with the specified name.

    All calls to this function with a given name return the same logger instance.
    This means that logger instances never need to be passed between different parts
    of an application.

    Args:
        name (str|None): specified name

    Returns:
        Logger: Return a logger with the specified name, or, if ``name`` is ``None``,
            return a logger which is the root logger of the hierarchy. If specified,
            the name is typically a dot-separated hierarchical name like ``a``, ``a.b``
            or ``a.b.c.d``. Choice of these names is entirely up to the developer
            who is using logging.
    """
    return getLogger(name)


def _prepare_logger(level, logger):
    """为设置日志处理器的函数准备参数"""
    level = level.upper()
    if not isinstance(logger, Logger):
        logger = get_logger(logger)
    if logger.level == logging.NOTSET:
        logger.setLevel(level)
    return level, logger


def setup_colored_handler(level='WARNING', logger=None):
    """为指定 logger 添加定向到 stderr 的彩色输出日志处理器。

    Args:
        level (str): 日志等级。
        logger (None|str|Logger): 日志器或其名称。
    """
    level, logger = _prepare_logger(level, logger)
    handler = StreamHandler()
    handler.setLevel(level)
    formatter = ColoredFormatter(DEFAULTS['LOG-FORMAT'],
                                 DEFAULTS['DATE-FORMAT'],
                                 DEFAULTS['LEVEL-STYLES'],
                                 DEFAULTS['FIELD-STYLES'])
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def setup_file_handler(filename, level='WARNING', logger=None):
    """设置保存在文件系统的日志。

    程序能够感知诸如 logrotate 对日志的处理并自动打开新的日志文件。

    Args:
        filename (str): 日志文件名。
        level (str): 日志等级。
        logger (None|str|Logger): 日志器或其名称。
    """
    level, logger = _prepare_logger(level, logger)
    handler = WatchedFileHandler(filename, 'a', encoding='utf8')
    handler.setLevel(level)
    formatter = logging.Formatter(DEFAULTS['LOG-FORMAT'],
                                  DEFAULTS['DATE-FORMAT'])
    handler.setFormatter(formatter)
    logger.addHandler(handler)
