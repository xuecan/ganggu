# -*- coding: UTF-8 -*-
# Copyright (C) 2012-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

from ganggu import httpkit as http
from ganggu.resolvecache import smart_url
import requests
import json
import pytest


# 有时候访问 httpbin.org 很慢（电信网络丢包严重）
http.TIMEOUT = (10.0, 30.0)


def test_get():
    url = 'http://httpbin.org/get'
    params = {'foo': 'bar'}
    resp = http.get(url, params=params)
    req = resp.request
    result = resp.json()
    assert resp.status_code == 200
    assert 'httpkit' in req.headers['User-Agent']
    assert result['url'] == url + '?foo=bar'


def test_debug_mode(capfd):
    # 参数 capfd 是 pytest 捕捉 stdout 和 stderr 输出的 fixture
    url = 'http://httpbin.org/get'
    with http.debug_mode():
        http.get(url)
    out, err = capfd.readouterr()
    assert 'GET /get HTTP/1.1' in out
    url2 = 'http://httpbin.org/ip'
    http.get(url2)
    assert 'GET /ip HTTP/1.1' not in out


def test_timeout():
    url = 'http://httpbin.org/delay/3'
    old_timeout = http.TIMEOUT
    http.TIMEOUT = (0.01, 10.0)
    with pytest.raises(requests.ConnectTimeout):
        resp = http.get(url)
    http.TIMEOUT = (5, 0.01)
    with pytest.raises(requests.ReadTimeout):
        resp = http.get(url)
    http.TIMEOUT = old_timeout


def test_post():
    url = 'http://httpbin.org/post'
    data = {'foo': 'bar'}
    resp = http.post(url, data=data)
    result = resp.json()
    assert result['form'] == data
    resp = http.post(url, json=data)
    result = resp.json()
    assert json.loads(result['data']) == data


def test_callable_url():
    url1 = 'http://httpbin.org/ip'
    url2 = smart_url(url1)
    resp1 = http.get(url1)
    resp2 = http.get(url2)
    assert resp1.text == resp2.text
