#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/12/25 下午3:11
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : crypto.py
# @Software: PyCharm
import uuid
import struct
import base64
import hashlib
from Crypto.Cipher import AES

__author__ = 'blackmatrix'


def generate_signature(access_token, encrypt_text, timestamp, nonce):
    sign = hashlib.sha1(''.join(sorted([access_token, timestamp, nonce, encrypt_text])).encode())
    return sign.hexdigest()


def check_signature(access_token, data, signature, timestamp, nonce):
    sign = generate_signature(access_token, data, timestamp, nonce)
    return sign == signature


def pcks7_unpad(text):
    """
    删除 PKCS#7 方式填充的字符串
    :param text:
    :return: str
    """
    return text[0: -ord(text[-1])]


def pcks7_pad(multiple, text):
    """
    :param multiple:
    :param text: str
    :return: str
    """
    return text + (multiple - len(text) % multiple) * chr(multiple - len(text) % multiple)


def decrypt(aes_key, ciphertext):
    aes_key = base64.b64decode(aes_key + '=')
    ciphertext = base64.b64decode(ciphertext)
    aes = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
    raw = aes.decrypt(ciphertext)
    return raw


def encrypt(aes_key, plaintext, key, buf=None):
    aes_key = base64.b64decode(aes_key + '=')
    buf = buf or str(uuid.uuid4()).replace('-', '')
    buf = buf[:16]
    length = struct.pack('!i', len(plaintext)).decode()
    aes = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
    encrypt_text = pcks7_pad(16, buf + length + plaintext + key)
    encrypt_text = aes.encrypt(encrypt_text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text


if __name__ == '__main__':
    pass
