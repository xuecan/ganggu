# -*- coding: UTF-8 -*-
# Copyright (C) 2012-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

from ganggu import httpkit as http
import requests
import json
import pytest


def test_get():
    url = 'https://httpbin.org/get'
    params = {'foo': 'bar'}
    resp = http.get(url, params=params)
    req = resp.request
    result = resp.json()
    assert resp.status_code == 200
    assert 'httpkit' in req.headers['User-Agent']
    assert result['url'] == url + '?foo=bar'


def test_debug_mode(capfd):
    url = 'https://httpbin.org/get'
    with http.debug_mode():
        resp = http.get(url)
    out, err = capfd.readouterr()
    assert 'GET /get HTTP/1.1' in out


def test_timeout():
    url = 'https://httpbin.org/delay/3'
    old_timeout = http.TIMEOUT
    http.TIMEOUT = (0.01, 10.0)
    with pytest.raises(requests.ConnectTimeout):
        resp = http.get(url)
    http.TIMEOUT = (5, 0.01)
    with pytest.raises(requests.ReadTimeout):
        resp = http.get(url)
    http.TIMEOUT = old_timeout


def test_post():
    url = 'https://httpbin.org/post'
    data = {'foo': 'bar'}
    resp = http.post(url, data=data)
    result = resp.json()
    assert result['form'] == data
    resp = http.post(url, json=data)
    result = resp.json()
    assert json.loads(result['data']) == data
