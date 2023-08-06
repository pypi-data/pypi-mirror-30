import logging
import random
import string

import codecs

try:
    from Crypto.Cipher import AES
    from Crypto.Hash import SHA256
except ImportError:
    from Cryptodome.Cipher import AES
    from Cryptodome.Hash import SHA256

logger = logging.getLogger(__name__)

TRUE_TUPLE = (True, 1, 'T', 't', 'True', 'ture', 'TURE', '1')
TRUE_AND_NONE_TUPLE = (None, True, 1, 'T', 't', 'True', 'ture', 'TURE', '1')


def add_padding(message, block_size=32):
    pad = block_size - (len(message) % block_size)
    return message + chr(pad) * pad


def remove_padding(message, block_size=32):
    pad = ord(message[-1])
    if pad < block_size:
        return message[:(-1 * pad):]
    return message


def encrypt_info(hash_key, hash_iv, info):
    aes = AES.new(hash_key, AES.MODE_CBC, hash_iv)

    padded_info = add_padding(info)
    encrypted_info_bytestr = aes.encrypt(padded_info)
    encrypted_info = codecs.encode(encrypted_info_bytestr, 'hex_codec')
    # encrypted_trade_info = ''.join('{:02x}'.format(ord(x)) for x in encrypted_trade_info_bytestr)

    return encrypted_info


def decrypt_info(hash_key, hash_iv, encrypted_info):
    aes = AES.new(hash_key, AES.MODE_CBC, hash_iv)

    encrypted_info_bytestr = codecs.decode(encrypted_info, 'hex_codec')
    padded_info = aes.decrypt(encrypted_info_bytestr)
    info = remove_padding(padded_info)

    return info


def generate_sha(hash_key, hash_iv, encrypted_info):
    hash = SHA256.new()

    hash.update('HashKey={}&{}&HashIV={}'.format(hash_key, encrypted_info, hash_iv).encode())
    trade_sha = hash.hexdigest().upper()

    return trade_sha


def validate_info(hash_key, hash_iv, info, sha):
    encrypted_info = encrypt_info(hash_key, hash_iv, info)
    info_sha = generate_sha(hash_key, hash_iv, encrypted_info)

    if sha != info_sha:
        return False
    return True


def generate_string(size):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))
