import binascii
from chardet.universaldetector import UniversalDetector as _UD # chardet module

def euckr_bytes_to_utf8_str(b):
    if type(b) is not bytes:
        raise TypeError('The %s is not bytes!' % (type(b)))
    return b.decode('euc-kr')

def bytes_to_str(b, encoding='utf-8'):
    if type(b) is not bytes:
        raise TypeError('The %s is not bytes!' % (type(b)))
    return b.decode(encoding)

def str_to_bytes(b, encoding='utf-8'):
    if type(b) is not str:
        raise TypeError('The %s is not str!' % (type(b)))
    return b.encode(encoding)

def bytes_to_hex(b):
    if type(b) is not bytes:
        raise TypeError('The %s is not bytes!' % (type(b)))
    return binascii.b2a_hex(b).decode('utf-8')

def hex_to_bytes(b):
    if type(b) is not str:
        raise TypeError('The %s is not str!' % (type(b)))
    return binascii.a2b_hex(b.encode('utf-8'))

def bytes_to_base64(b):
    if type(b) is not bytes:
        raise TypeError('The %s is not bytes!' % (type(b)))
    return binascii.b2a_base64(b, newline=False).decode('utf-8')

def base64_to_bytes(b):
    if type(b) is not str:
        raise TypeError('The %s is not str!' % (type(b)))
    return binascii.a2b_base64(b.encode('utf-8'))

def detect_encoding(s):
    if type(s) is not bytes:
        raise TypeError('The %s is not bytes!' % (type(s)))
    
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
