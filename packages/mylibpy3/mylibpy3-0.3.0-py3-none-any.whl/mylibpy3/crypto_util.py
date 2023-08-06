import hashlib as _hashlib
from .aes import SimpleAes as _SimpleAes
from . import codec_util as _cu

def sha256(s):
    return _cu.bytes_to_hex(_hashlib.sha256(_cu.str_to_bytes(s)).digest())

def encrypt_aes(s):
    return _cu.bytes_to_hex(_SimpleAes().encrypt(_cu.str_to_bytes(s)))

def decrypt_aes(hex):
    return _cu.bytes_to_str(_SimpleAes().decrypt(_cu.hex_to_bytes(hex)))

if __name__ == '__main__':
    pass
