#-*- coding: utf-8 -*-
import pyaes as _pyaes # pyaes module

# 패딩은 PKCS5Padding 표준
def _Pkcs5Padding(s, block_byte_size):
    needed_pad_byte_size = block_byte_size - len(s) % block_byte_size
    return s + (needed_pad_byte_size) * chr(needed_pad_byte_size)

def _unPkcs5Padding(s):
    return s[:-ord(s[len(s)-1:])]


# 보통 자주 쓰는게 AES128/CBC/PKCS5Padding
class Aes128CbcEncryptor(object):
    def __init__(self, key, iv):
        self._block_byte_size = 16
        if len(key) >= self._block_byte_size:
            self._key = key[:self._block_byte_size]
        else:
            self._key = _Pkcs5Padding(key, self._block_byte_size)
        if len(iv) >= self._block_byte_size:
            self._iv = iv[:self._block_byte_size]
        else:
            self._iv = _Pkcs5Padding(iv, self._block_byte_size)
        
        self._encryptor = _pyaes.Encrypter(_pyaes.AESModeOfOperationCBC(self._key, iv = self._iv))
    
    def encrypt(self, dec):
        # feed has auto padding
        enc = self._encryptor.feed(dec)
        enc += self._encryptor.feed()
        return enc


class Aes128CbcDecryptor(object):
    def __init__(self, key, iv):
        self._block_byte_size = 16
        if len(key) >= self._block_byte_size:
            self._key = key[:self._block_byte_size]
        else:
            self._key = _Pkcs5Padding(key, self._block_byte_size)
        if len(iv) >= self._block_byte_size:
            self._iv = iv[:self._block_byte_size]
        else:
            self._iv = _Pkcs5Padding(iv, self._block_byte_size)
        
        self._decryptor = _pyaes.Decrypter(_pyaes.AESModeOfOperationCBC(self._key, iv = self._iv))
    
    def decrypt(self, enc):
        # feed has auto padding
        dec = self._decryptor.feed(enc)
        dec += self._decryptor.feed()
        return dec


# CBC 모드는 같은 값이 반복되어도 값이 달라지므로 stream에 적합하고,
# ECB 모드는 같은 값이 반복되면 결과 역시 반복되므로 간단한 처리에 적합. ECB는 iv가 불필요
# AES128/ECB/PKCS5Padding
class Aes128Ecb(object):
    def __init__(self, key):
        self._block_byte_size = 16
        if len(key) >= self._block_byte_size:
            self._key = key[:self._block_byte_size]
        else:
            self._key = _Pkcs5Padding(key, self._block_byte_size)
        
        self._cryptor = _pyaes.AESModeOfOperationECB(self._key)
    
    def encrypt(self, dec):
        dec = _Pkcs5Padding(dec, self._block_byte_size)
        enc = ''
        index = 0
        length = len(dec)
        while index < length:
          enc += self._cryptor.encrypt(dec[index:index+self._block_byte_size])
          index += self._block_byte_size
        return enc

    def decrypt(self, enc):
        dec = ''
        index = 0
        length = len(enc)
        while index < length:
          dec += self._cryptor.decrypt(enc[index:index+self._block_byte_size])
          index += self._block_byte_size
        return _unPkcs5Padding(dec)


class SimpleAes(Aes128Ecb):
    def __init__(self):
      super(SimpleAes, self).__init__('')


if __name__ == '__main__':
    pass
