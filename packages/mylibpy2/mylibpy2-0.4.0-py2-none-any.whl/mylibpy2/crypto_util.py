#-*- coding: utf-8 -*-
import hashlib as _hashlib
from .aes import SimpleAes as _SimpleAes
from . import codec_util as _cu

def sha256(u):
    return _cu.str_to_hex(_hashlib.sha256(_cu.unicode_to_str(u)).digest())

def encrypt_aes(u):
    return _cu.str_to_hex(_SimpleAes().encrypt(_cu.unicode_to_str(u)))

def decrypt_aes(hex):
    return _cu.str_to_unicode(_SimpleAes().decrypt(_cu.hex_to_str(hex)))

if __name__ == '__main__':
    pass
