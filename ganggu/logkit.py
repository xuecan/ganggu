# -*- coding: UTF-8 -*-
# Copyright (C) 2012-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
# 日志工具

加载本模块后，将会扩展 Python 标准库的日志等级如下：

+-----------+-------+-----------------------------------+
| Level     | Value | Defined                           |
+-----------+-------+-----------------------------------+
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

使用 `Logger(name)` 代替标准库的 `getLogger(name)`。可以使用方便的
`emergency()`、`alert()`、`notice()`、`verbose()` 和 `spam()` 方法。

依赖：

  * [coloredlogs](https://coloredlogs.readthedocs.io/en/latest/)
"""

import logging
import coloredlogs
from logging import getLogger as get_logger

__version__ = '1.0.0'


DEFAULTS = {
    # coloredlogs default:
    'LOG-FORMAT': '%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s',
    # 日期格式
    'DATE-FORMAT': '%Y-%m-%d %H:%M:%S',
    # 字段样式
    'FIELD-STYLES': {
        'hostname':    {'color': 'magenta'},
        'programname': {'color': 'blue'},
        'name':        {'color': 'cyan'},
        'levelname':   {'color': 'black', 'bold': True},
        'asctime':     {'color': 'green'},
    },
    # 等级样式
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


def add_log_level(value, name):
    """为 logging 标准库注入新的日志等级"""
    logging.addLevelName(value, name)
    setattr(logging, name, value)


# 在 DEBUG 和 INFO 之间增加 SPAM 级别(兼容 verboselogs 1.1)
add_log_level(5, 'SPAM')

# 在 INFO 和 DEBUG 之间增加 VERBOSE 级别(兼容 verboselogs 1.0)
add_log_level(15, 'VERBOSE')

# 在 WARNING 和 INFO 之间增加 NOTICE 级别(兼容 RFC 5424)
add_log_level(25, 'NOTICE')

# 增加 ALERT 级别(兼容 RFC 5424)
add_log_level(60, 'ALERT')

# 增加 EMERGENCY 级别(兼容 RFC 5424)
add_log_level(70, 'EMERGENCY')


class Logger(logging.Logger):
    """日志器"""

    def __init__(self, *args, **kw):
        logging.Logger.__init__(self, *args, **kw)
        self.parent = logging.getLogger()

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


logging.setLoggerClass(Logger)


def setup_console_logger(level='DEBUG'):
    """设置在终端输出的日志"""
    settings = {
        'fmt':          DEFAULTS['LOG-FORMAT'],
        'datefmt':      DEFAULTS['DATE-FORMAT'],
        'field_styles': DEFAULTS['FIELD-STYLES'],
        'level_styles': DEFAULTS['LEVEL-STYLES'],
    }
    coloredlogs.install(level, **settings)


def setup_logger(level, filename, logger=None):
    """设置保存在文件系统的日志"""
    level = level.upper()
    try:
        from . import httpkit
        if level == 'SPAM':
            httpkit.set_debug_level(2)
        elif level == 'DEBUG':
            httpkit.set_debug_level(1)
        else:
            httpkit.set_debug_level(0)
    except ImportError:
        pass
    if not logger:
        logger = logging.getLogger()
    logger.setLevel(level)
    logger.propagate = True
    setup_console_logger(level)
    if not filename:
        return
    handler = logging.FileHandler(filename, 'a', encoding='utf8')
    handler.setLevel(level)
    formatter = logging.Formatter(DEFAULTS['LOG-FORMAT'],
                                  DEFAULTS['DATE-FORMAT'])
    handler.setFormatter(formatter)
    logger.addHandler(handler)
