# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

import logging
import shutil
from ganggu import logkit


def test_get_logger():
    logger1 = logkit.get_logger()
    logger2 = logging.getLogger()
    assert logger1 is logger2, '同名的日志器应该是同一个实例'
    assert isinstance(logger1, logkit.Logger), '应该得到 logkit.Logger 的实例'


def test_colored_handler(capfd):
    # 参数 capfd 是 pytest 捕捉 stdout 和 stderr 输出的 fixture
    logger = logkit.get_logger('test')
    logger.clearHandlers()
    logkit.setup_colored_handler('INFO', logger)
    logger.info('Foo!')
    out, err = capfd.readouterr()
    assert 'INFO' in err and 'Foo!' in err, '输出到 stderr 的日志存在问题'
    logger.debug('Bar!')
    out, err = capfd.readouterr()
    assert err == '', 'DEBUG 级别的日志不应被输出'


def test_file_handler(tmpdir):
    # 参数 tmpdir 是 pytest 与临时文件相关的 fixture
    logfile = tmpdir.join('test.log')
    filename = logfile.strpath
    logger = logkit.get_logger('test')
    logger.clearHandlers()
    logkit.setup_file_handler(filename, 'INFO', logger)
    logger.info('Foo!')
    logger.debug('Bar!')
    content = logfile.read()
    assert 'Foo!' in content, 'INFO 级别的信息应该被写入日志'
    assert 'Bar!' not in content, 'DEBUG 级别的日志不应被写入日志'
    rotated = filename + '.1'
    shutil.move(filename, rotated)
    logger.info('Foobar!')
    content = logfile.read()
    assert 'Foo!' not in content, '旧日志应该已经被移走了'
    assert 'Foobar!' in content, '新日志应被写入日志文件名指向的文件'
