# -*- coding: UTF-8 -*-
# Copyright (C) 2012-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
HTTP 工具包
===========

本模块简单封装了 requests 包，提供了默认的超时设置和一些调试需要的工具。

本模块依赖如下第三方库：

* `requests <http://docs.python-requests.org/en/master/>`_
"""

import http.client
import logging
import contextlib
from . import logkit  # logkit 需要在 requests 之前被 import
import requests
from platform import python_version

__all__ = ['debug_on', 'debug_off', 'debug_mode', 'Session',
           'get', 'options', 'head', 'post', 'put', 'patch', 'delete',
           'GET', 'OPTIONS', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE']

__version__ = '1.1.0'


# timeouts in seconds: (connect_timeout, read_timeout)
TIMEOUT = (5.0, 10.0)

# logger of requests
LOGGER = logkit.get_logger('requests.packages.urllib3')


def debug_on():
    """Turn on logging of the requests module."""
    http.client.HTTPConnection.debuglevel = 1
    LOGGER.setLevel(logging.DEBUG).setPropagate(True)


def debug_off():
    """Turn off logging of the requests module."""
    http.client.HTTPConnection.debuglevel = 0
    LOGGER.setLevel(logging.WARNING).setPropagate(False)


@contextlib.contextmanager
def debug_mode():
    """Logging of the requests module context."""
    debug_on()
    yield
    debug_off()


def _default_user_agent():
    return 'ganggu.httpkit/%s requests/%s python/%s' % \
           (__version__, requests.__version__, python_version())


def setup_default_user_agent(callback=None):
    """Setup default user agent.

    Args:
        callback (callable): A callable returns a string representing
                             the default user agent.
    """
    requests.utils.default_user_agent = callback or _default_user_agent


setup_default_user_agent()


class Session(requests.Session):

    def request(self, method, url, params=None, data=None, headers=None,
                cookies=None, files=None, auth=None, timeout=None,
                allow_redirects=True, proxies=None, hooks=None, stream=None,
                verify=None, cert=None, json=None):
        """Constructs and sends an HTTP request.

        Args:
            method (str): Method for the request.
            url (str): URL for the request.
            params (bytes|dict): Dictionary or bytes to be sent in the query
                                 string for the request.
            data (bytes|dict|file): Dictionary, bytes, or file-like object to send
                                    in the body of the request.
            json (dict|list): JSON to send in the body of the request.
            headers (dict): Dictionary of HTTP Headers to send with the request.
            cookies (dict|CookieJar): Dict or CookieJar object to send with the request.
            files (dict): Dictionary of ``'filename': file-like-objects``
                          for multipart encoding upload.
            auth (tuple|callable): Auth tuple or callable to enable
                                   Basic/Digest/Custom HTTP Auth.
            timeout (float|tuple): How long to wait for the server to send
                                   data before giving up, as a float, or a (float, float) tuple.
            allow_redirects (bool):  Set to True by default.
            proxies (dict): Dictionary mapping protocol or protocol and
                            hostname to the URL of the proxy.
            stream (bool): Whether to immediately download the response
                           content. Defaults to ``False``.
            verify (bool): Whether the SSL cert will be verified.
                           A CA_BUNDLE path can also be provided. Defaults to ``True``.
            cert (str|tuple): If String, path to ssl client cert file (.pem).
                              If Tuple, ('cert', 'key') pair.
            hooks (dict): Event hooks.

        Returns:
            requests.Response: HTTP response.
        """
        if not timeout:
            timeout = TIMEOUT
        return super(Session, self).request(method, url, params, data, headers,
                                            cookies, files, auth, timeout,
                                            allow_redirects, proxies, hooks, stream,
                                            verify, cert, json)


def request(method, url, **kwargs):
    """Constructs and sends an HTTP request.

    Args:
        method (str): Method for the request.
        url (str): URL for the request.
        \*\*kwargs: Optional arguments that ``Session.request()`` takes.

    Returns:
        requests.Response: HTTP response.
    """
    # By using the 'with' statement we are sure the session is closed, thus we
    # avoid leaving sockets open which can trigger a ResourceWarning in some
    # cases, and look like a memory leak in others.
    with Session() as session:
        return session.request(method, url, **kwargs)


def get(url, params=None, **kwargs):
    """Sends a GET request.

    Args:
        url (str): URL for the request.
        params (bytes|dict): Dictionary or bytes to be sent in the query string
                             for the request.
        \*\*kwargs: Optional arguments that ``Session.request()`` takes.

    Returns:
        requests.Response: HTTP response.
    """
    kwargs.setdefault('allow_redirects', True)
    return request('get', url, params=params, **kwargs)


def options(url, **kwargs):
    """Sends a OPTIONS request.

    Args:
        url (str): URL for the request.
        \*\*kwargs: Optional arguments that ``Session.request()`` takes.

    Returns:
        requests.Response: HTTP response.
    """
    kwargs.setdefault('allow_redirects', True)
    return request('options', url, **kwargs)


def head(url, **kwargs):
    """Sends a HEAD request.

    Args:
        url (str): URL for the request.
        \*\*kwargs: Optional arguments that ``Session.request()`` takes.

    Returns:
        requests.Response: HTTP response.
    """
    kwargs.setdefault('allow_redirects', False)
    return request('head', url, **kwargs)


def post(url, data=None, json=None, **kwargs):
    """Sends a POST request.

    Args:
        url (str): URL for the request.
        data (bytes|dict|file): Dictionary, bytes, or file-like object to send in the body of
                                the request.
        json (dict|list): JSON data to send in the body of the request.
        \*\*kwargs: Optional arguments that ``Session.request()`` takes.

    Returns:
        requests.Response: HTTP response.
    """
    return request('post', url, data=data, json=json, **kwargs)


def put(url, data=None, **kwargs):
    """Sends a PUT request.

    Args:
        url (str): URL for the request.
        data (bytes|dict|file): Dictionary, bytes, or file-like object to send in the body of
                                the request.
        \*\*kwargs: Optional arguments that ``Session.request()`` takes.

    Returns:
        requests.Response: HTTP response.
    """
    return request('put', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    """Sends a PATCH request.

    Args:
        url (str): URL for the request.
        data (bytes|dict|file): Dictionary, bytes, or file-like object to send in the body of
                                the request.
        \*\*kwargs: Optional arguments that ``Session.request()`` takes.

    Returns:
        requests.Response: HTTP response.
    """
    return request('patch', url,  data=data, **kwargs)


def delete(url, **kwargs):
    """Sends a DELETE request.

    Args:
        url (str): URL for the request.
        \*\*kwargs: Optional arguments that ``Session.request()`` takes.

    Returns:
        requests.Response: HTTP response.
    """
    return request('delete', url, **kwargs)


# upper case
GET = get
OPTIONS = options
HEAD = head
POST = post
PUT = put
PATCH = patch
DELETE = delete
