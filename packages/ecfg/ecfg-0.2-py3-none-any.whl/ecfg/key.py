import binascii
import os
import pathlib


def read_private_key(path: pathlib.Path) -> str:
    with path.open():
        data = path.read_text()

    private_key = binascii.unhexlify(data.strip())

    if len(private_key) != 32:
        raise IOError('invalid private key')

    return private_key


def load_private_key(public_key: str) -> str:

    default_keydir = '/opt/ejson/keys'
    keydir = os.environ.get('EJSON_KEYDIR', default_keydir)

    path = pathlib.Path(keydir).joinpath(public_key)
    return read_private_key(path)
