#-*- coding: utf-8 -*-
from chardet.universaldetector import UniversalDetector as _UD # chardet module

def euckr_str_to_utf8_unicode(b):
    if type(b) is not str:
        raise TypeError('The %s is not str!' % (type(b)))
    return b.decode('euc-kr')

def str_to_unicode(b, encoding='utf-8'):
    if type(b) is not str:
        raise TypeError('The %s is not str!' % (type(b)))
    return b.decode(encoding)

def unicode_to_str(b, encoding='utf-8'):
    if type(b) is not unicode:
        raise TypeError('The %s is not unicode!' % (type(b)))
    return b.encode(encoding)

def str_to_hex(b):
    if type(b) is not str:
        raise TypeError('The %s is not str!' % (type(b)))
    return b.encode('hex').decode('utf-8')

def hex_to_str(b):
    if type(b) is not unicode:
        raise TypeError('The %s is not unicode!' % (type(b)))
    return b.encode('utf-8').decode('hex')

def str_to_base64(b):
    if type(b) is not str:
        raise TypeError('The %s is not str!' % (type(b)))
    return b.encode('base64').replace('\n', '').decode('utf-8')

def base64_to_str(b):
    if type(b) is not unicode:
        raise TypeError('The %s is not unicode!' % (type(b)))
    return b.encode('utf-8').decode('base64')

def detect_encoding(s):
    if type(s) is not str:
        raise Exception('The %s is not str!' % (type(s)))
    
    detector = _UD()

    length = len(s)
    interval = length // 100
    if interval <= 100: interval = 100
    i = 0
    while i < length:
        detector.feed(s[i:i+interval])
        i += interval
        if detector.done: break
    detector.close()
    if i > length: i = length

    result = detector.result
    result['size'] = length
    result['detected_at'] = i
    return result

if __name__ == '__main__':
    pass
