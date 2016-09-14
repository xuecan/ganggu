# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
# 一组配合 Flask 的实用工具

依赖：

* Flask
"""

__all__ = ['render_template', 'url_for', 'jsonify', 'urlize',
           'redirect', 'js_redirect', 'abort', 'json_abort',
           'JsonAbort', 'register_json_abort_handler']

import urllib
from flask import render_template, url_for, abort, jsonify, redirect
from werkzeug.wrappers import BaseResponse
from werkzeug.utils import escape
from werkzeug.http import HTTP_STATUS_CODES


def js_redirect(location, template=None):
    """类似 flask.redirect，但是使用 JavaScript 实现而非 HTTP 30x 重定向机制"""
    display_location = escape(location)
    if isinstance(location, str):
        from werkzeug.urls import iri_to_uri
        location = iri_to_uri(location)
    href = location
    if not template:
        response = BaseResponse(
            u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
            u'<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n'
            u'<TITLE>Loading...</TITLE>\n'
            u'<P>&nbsp;</P><P>&nbsp;</P><P>&nbsp;</P><P>&nbsp;</P><P>&nbsp;</P>\n'
            u'<P ALIGN="center"><A HREF="%(location)s"></A></P>\n'
            u'<SCRIPT>document.location.href="%(location)s";</SCRIPT>' %
            {'location': href, 'display_location': display_location}, 200,
            mimetype='text/html')
        #response.headers['Location'] = location
        return response
    else:
        return render_template(template, location=href,
                               display_location=display_location)


def urlize(key, value, encoding='utf8'):
    """生成可用于 URL 中的 key=value 片段"""
    if isinstance(value, unicode):
        value = value.encode(encoding)
    return urllib.urlencode({key: value})


class JsonAbort(Exception):

    def __init__(self, status_code=200, message=None, payload=None):
        if not message:
            message = HTTP_STATUS_CODES[status_code]
        Exception.__init__(self, '%d %s' % (status_code, message))
        self.status_code = status_code
        self.message = message
        self.payload = payload or dict()

    def to_dict(self):
        return self.payload


def _handle_json_abort(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def register_json_abort_handler(app):
    app.register_error_handler(JsonAbort, _handle_json_abort)


def json_abort(status_code=200, message=None, payload=None):
    raise JsonAbort(status_code, message, payload)
