from base64 import b64decode
try:
    basestring
except NameError:
    basestring = str

from nacl.public import Box, PrivateKey, PublicKey


def decrypt_message(msg, private_key):
    header, b64_encpub, b64_nonce, b64_box = msg.split(':')
    encpub = b64decode(b64_encpub)
    nonce = b64decode(b64_nonce)
    box = b64decode(b64_box)

    b = Box(PrivateKey(private_key), PublicKey(encpub))

    decrypted = b.decrypt(box, nonce)
    return decrypted.decode('utf-8')


def decrypt_dict(d, private_key):
    def process(name, value):
        if isinstance(value, dict):
            return decrypt_dict(value, private_key)
        if isinstance(value, basestring) and not name.startswith('_'):
            return decrypt_message(value, private_key)
        return value

    return {name: process(name, value) for name, value in d.items()}
