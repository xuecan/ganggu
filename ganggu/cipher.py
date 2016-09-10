# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://opensource.org/licenses/mit-license

import hmac
from Crypto.Cipher import AES, DES3


def hmac_digest(data, key, method='sha256'):
    return hmac.new(key, data, method).hexdigest()


def pkcs5_pad(data, block_size):
    if not isinstance(data, bytes):
        raise ValueError('first argument sould be bytes')
    pad_len = block_size - len(data) % block_size # length of padding
    padding = chr(pad_len).encode('ascii') * pad_len # PKCS5 padding content
    data += padding
    return data


def pkcs5_unpad(data):
    if not isinstance(data, bytes):
        raise ValueError('first argument sould be bytes')
    pad_len = ord(data[-1:])
    data = data[:-pad_len]
    return data


def aes_encrypt(data, key, iv):
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    data = pkcs5_pad(data, AES.block_size)
    return encryptor.encrypt(data)


def aes_decrypt(data, key, iv):
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    data = encryptor.decrypt(data)
    data = pkcs5_unpad(data)
    return data


def des3_encrypt(data, key, iv):
    encryptor = DES3.new(key, iv)
    data = pkcs5_pad(data, DES3.block_size)
    return encryptor.encrypt(data)


def des3_decrypt(data, key, iv):
    encryptor = DES3.new(key, iv)
    data = encryptor.decrypt(data)
    data = pkcs5_unpad(data)
    return data
