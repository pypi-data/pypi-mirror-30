# -*- coding: utf-8 -*-
"""
create on 2018-03-29 上午12:04

author @heyao
"""
from Crypto.Cipher import AES


def encrypt(content, key, iv):
    obj = AES.new(key, AES.MODE_CBC, iv)
    if hasattr(content, 'encode'):
        content = content.encode('utf-8')
    add_s = b'\n' * (16 - len(content) % 16)
    return obj.encrypt(content + add_s)


def decrypt(ciphertext, key, iv):
    obj = AES.new(key, AES.MODE_CBC, iv)
    return obj.decrypt(ciphertext).strip()
