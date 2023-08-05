import binascii
import os


def read_private_key(path):
    with open(path) as fh:
        data = fh.read()

    private_key = binascii.unhexlify(data.strip())

    if len(private_key) != 32:
        raise IOError('invalid private key')

    return private_key


def load_private_key(public_key):
    default_keydir = '/opt/ejson/keys'
    keydir = os.environ.get('EJSON_KEYDIR', default_keydir)

    path = os.path.join(keydir, public_key)
    return read_private_key(path)
