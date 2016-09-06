# -*- coding: UTF-8 -*-
# Copyright (C) 2012-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

"""
## HTTP Kit

面向 [python-requests][] 的简单封装，使用了更为合理的超时设置。并修正了其依赖的
[http.client][] 标准库中关于调试的一些设置。

[python-requests]: http://docs.python-requests.org/en/latest/
[http.client]: https://docs.python.org/3/library/http.client.html

### 补丁说明

Requests 库依赖标准库 [http.client.HTTPConnection][]，其中包含了 `debuglevel`
属性，标准库中的实现当 `debuglevel` 不为 `0` 时开启调试，会直接向 stdout 输出调试信息。
运用了补丁之后，将会：

* 使用日志机制输出调试信息，这样可以输出到 stderr 或日志文件中；
* 支持两级的调试，当 `debuglebel` 为 `1` 时，输出的信息与标准库默认的一样，即输出除了
  HTTP 响应正文之外的各类信息。大于 `1` 时，额外输出响应正文。

[http.client.HTTPConnection]: https://docs.python.org/3/library/http.client.html#httpconnection-objects

----

Working for Requests 2.11.1 and Python 3.5.0 .

依赖：

  * [requests](http://docs.python-requests.org/en/master/)
"""

import http.client
import requests
from . import logkit


__all__ = ["patch_http_client", "set_debug_level",
           "get", "options", "head", "post", "put", "patch", "delete",
           "GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"]

__version__ = '1.0.0'

# User-Agent
USER_AGENT = requests.utils.default_user_agent()

# timeouts in seconds: (connect_timeout, read_timeout)
TIMEOUT = (5.0, 10.0)

# logger for this module
LOGGER = logkit.Logger('HTTPKIT')
LOGGER.propagate = True


def set_debug_level(level):
    """设置调试信息等级。

      - 0: 不显示调试信息
      - 1: 显示大部分用于调试的信息，除了响应报文
      - 2: 比 1 增加响应报文
    """
    http.client.HTTPConnection.debuglevel = int(level)


# ====================================================================== #
#                              Wrappers                                  #
# ====================================================================== #

def request(method, url, **kwargs):
    """Constructs and sends a :class:`Request <Request>`.

    :param method: method for the new :class:`Request` object.
    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
        to add for the file.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How long to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :type timeout: float or tuple
    :param allow_redirects: (optional) Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
    :type allow_redirects: bool
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) whether the SSL cert will be verified. A CA_BUNDLE path can also be provided. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response

    Usage::

      >>> import requests
      >>> req = requests.request('GET', 'http://httpbin.org/get')
      <Response [200]>
    """
    kwargs.setdefault("timeout", TIMEOUT)
    # By using the 'with' statement we are sure the session is closed, thus we
    # avoid leaving sockets open which can trigger a ResourceWarning in some
    # cases, and look like a memory leak in others.
    with requests.Session() as session:
        return session.request(method=method, url=url, **kwargs)
    if http.client.HTTPConnection.debuglevel > 1:
        LOGGER.spam("RESPONSE CONTENT:\n" + repr(response.content))
    return response


def get(url, params=None, **kwargs):
    """Sends a GET request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs.setdefault('allow_redirects', True)
    return request('get', url, params=params, **kwargs)


def options(url, **kwargs):
    """Sends a OPTIONS request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs.setdefault('allow_redirects', True)
    return request('options', url, **kwargs)


def head(url, **kwargs):
    """Sends a HEAD request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs.setdefault('allow_redirects', False)
    return request('head', url, **kwargs)


def post(url, data=None, json=None, **kwargs):
    """Sends a POST request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return request('post', url, data=data, json=json, **kwargs)


def put(url, data=None, **kwargs):
    """Sends a PUT request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return request('put', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    """Sends a PATCH request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return request('patch', url,  data=data, **kwargs)


def delete(url, **kwargs):
    """Sends a DELETE request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
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


# ====================================================================== #
#                                Patches                                 #
# ====================================================================== #

# 针对 http.client 与 debuglevel 相关的补丁，运用之后使用日志机制显示调试信息

# symbols used in patch methods
import os
import collections
from http.client import (_MAXLINE, LineTooLong, RemoteDisconnected,
                         BadStatusLine, UnknownProtocol, parse_headers,
                         NO_CONTENT, NOT_MODIFIED, NotConnected,
                         _METHODS_EXPECTING_BODY, CONTINUE, HTTPMessage,
                         IncompleteRead)


# based on python 3.5.0
def _HTTPResponse__read_status(self):
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
    if len(line) > _MAXLINE:
        raise LineTooLong("status line")
    if self.debuglevel > 0:
        LOGGER.debug("REPLY: " + repr(line))  # HACKED!
    if not line:
        # Presumably, the server closed the connection before
        # sending a valid response.
        raise RemoteDisconnected("Remote end closed connection without"
                                 " response")
    try:
        version, status, reason = line.split(None, 2)
    except ValueError:
        try:
            version, status = line.split(None, 1)
            reason = ""
        except ValueError:
            # empty version will cause next test to fail.
            version = ""
    if not version.startswith("HTTP/"):
        self._close_conn()
        raise BadStatusLine(line)

    # The status code is a three-digit number
    try:
        status = int(status)
        if status < 100 or status > 999:
            raise BadStatusLine(line)
    except ValueError:
        raise BadStatusLine(line)
    return version, status, reason


# based on python 3.5.0
def _HTTPResponse_begin(self):
    if self.headers is not None:
        # we've already started reading the response
        return

    # read until we get a non-100 response
    while True:
        version, status, reason = self._read_status()
        if status != CONTINUE:
            break
        # skip the header from the 100 response
        while True:
            skip = self.fp.readline(_MAXLINE + 1)
            if len(skip) > _MAXLINE:
                raise LineTooLong("header line")
            skip = skip.strip()
            if not skip:
                break
            if self.debuglevel > 0:
                LOGGER.debug("HEADER: " + skip)  # HACKED!

    self.code = self.status = status
    self.reason = reason.strip()
    if version in ("HTTP/1.0", "HTTP/0.9"):
        # Some servers might still return "0.9", treat it as 1.0 anyway
        self.version = 10
    elif version.startswith("HTTP/1."):
        self.version = 11   # use HTTP/1.1 code for HTTP/1.x where x>=1
    else:
        raise UnknownProtocol(version)

    self.headers = self.msg = parse_headers(self.fp)

    if self.debuglevel > 0:
        buf = "PARSED HEADERS:"  # HACKED!
        for hdr in self.headers:
            buf += "\n  " + hdr + ": " + self.headers[hdr]  # HACKED!
        LOGGER.debug(buf)  # HACKED!

    # are we using the chunked-style of transfer encoding?
    tr_enc = self.headers.get("transfer-encoding")
    if tr_enc and tr_enc.lower() == "chunked":
        self.chunked = True
        self.chunk_left = None
    else:
        self.chunked = False

    # will the connection close at the end of the response?
    self.will_close = self._check_close()

    # do we have a Content-Length?
    # NOTE: RFC 2616, S4.4, #3 says we ignore this if tr_enc is "chunked"
    self.length = None
    length = self.headers.get("content-length")

     # are we using the chunked-style of transfer encoding?
    tr_enc = self.headers.get("transfer-encoding")
    if length and not self.chunked:
        try:
            self.length = int(length)
        except ValueError:
            self.length = None
        else:
            if self.length < 0:  # ignore nonsensical negative lengths
                self.length = None
    else:
        self.length = None

    # does the body have a fixed length? (of zero)
    if (status == NO_CONTENT or status == NOT_MODIFIED or
        100 <= status < 200 or      # 1xx codes
        self._method == "HEAD"):
        self.length = 0

    # if the connection remains open, and we aren't using chunked, and
    # a content-length was not provided, then assume that the connection
    # WILL close.
    if (not self.will_close and
        not self.chunked and
        self.length is None):
        self.will_close = True


# based on python 3.5.0
def _HTTPConnection_send(self, data):
    """Send `data' to the server.
    ``data`` can be a string object, a bytes object, an array object, a
    file-like object that supports a .read() method, or an iterable object.
    """

    if self.sock is None:
        if self.auto_open:
            self.connect()
        else:
            raise NotConnected()

    if self.debuglevel > 0:
        LOGGER.debug("SEND: " + repr(data.decode("iso-8859-1")))  # HACKED!
    blocksize = 8192
    if hasattr(data, "read") :
        if self.debuglevel > 0:
            LOGGER.debug("sendIng a read()able")  # HACKED!
        encode = False
        try:
            mode = data.mode
        except AttributeError:
            # io.BytesIO and other file-like objects don't have a `mode`
            # attribute.
            pass
        else:
            if "b" not in mode:
                encode = True
                if self.debuglevel > 0:
                    LOGGER.debug("encoding file using iso-8859-1")  # HACKED!
        while 1:
            datablock = data.read(blocksize)
            if not datablock:
                break
            if encode:
                datablock = datablock.encode("iso-8859-1")
            self.sock.sendall(datablock)
        return
    try:
        self.sock.sendall(data)
    except TypeError:
        if isinstance(data, collections.Iterable):
            for d in data:
                self.sock.sendall(d)
        else:
            raise TypeError("data should be a bytes-like object "
                            "or an iterable, got %r" % type(data))


# based on python 3.5.0
def _HTTPConnection__set_content_length(self, body, method):
    # Set the content-length based on the body. If the body is "empty", we
    # set Content-Length: 0 for methods that expect a body (RFC 7230,
    # Section 3.3.2). If the body is set for other methods, we set the
    # header provided we can figure out what the length is.
    thelen = None
    method_expects_body = method.upper() in _METHODS_EXPECTING_BODY
    if body is None and method_expects_body:
        thelen = '0'
    elif body is not None:
        try:
            thelen = str(len(body))
        except TypeError:
            # If this is a file-like object, try to
            # fstat its file descriptor
            try:
                thelen = str(os.fstat(body.fileno()).st_size)
            except (AttributeError, OSError):
                # Don't send a length if this failed
                if self.debuglevel > 0:
                    LOGGER.debug("Cannot stat!!")  # HACKED!

    if thelen is not None:
        self.putheader('Content-Length', thelen)


# based on python 3.5.0
def _HTTPConnection__tunnel(self):
    connect_str = "CONNECT %s:%d HTTP/1.0\r\n" % (self._tunnel_host,
        self._tunnel_port)
    connect_bytes = connect_str.encode("ascii")
    self.send(connect_bytes)
    for header, value in self._tunnel_headers.items():
        header_str = "%s: %s\r\n" % (header, value)
        header_bytes = header_str.encode("latin-1")
        self.send(header_bytes)
    self.send(b'\r\n')

    response = self.response_class(self.sock, method=self._method)
    (version, code, message) = response._read_status()

    if code != http.HTTPStatus.OK:
        self.close()
        raise OSError("Tunnel connection failed: %d %s" % (code,
                                                           message.strip()))
    while True:
        line = response.fp.readline(_MAXLINE + 1)
        if len(line) > _MAXLINE:
            raise LineTooLong("header line")
        if not line:
            # for sites which EOF without sending a trailer
            break
        if line in (b'\r\n', b'\n', b''):
            break

        if self.debuglevel > 0:
            LOGGER.debug('HEADER: ' + line.decode())  # HACKED!


def patch_http_client():
    """运用与 debuglevel 相关的补丁"""
    http.client.HTTPResponse._read_status = _HTTPResponse__read_status
    http.client.HTTPResponse.begin = _HTTPResponse_begin
    http.client.HTTPConnection.send = _HTTPConnection_send
    http.client.HTTPConnection._set_content_length = _HTTPConnection__set_content_length
    http.client.HTTPConnection._tunnel = _HTTPConnection__tunnel


patch_http_client()
