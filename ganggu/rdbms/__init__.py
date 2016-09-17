# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

from sqlalchemy import create_engine


def make_engine(uri, debug=False):
    if not uri.startswith("mysql+pymysql://"):
        raise ValueError("not for MySQL")
    engine = create_engine(
        uri,
        encoding="utf-8",
        paramstyle="pyformat",
        isolation_level="READ COMMITTED",
        echo=debug
    )
    return engine
