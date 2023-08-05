import json
import os

from .crypto import decrypt_dict
from .key import load_private_key


def load(path: str) -> dict:
    """Decrypt a ejson file, return the decrypted dict.

    The private key will be loaded from:
    - $EJSON_KEYDIR if present
    - /opt/ejson/keys
    """
    with open(path) as fh:
        content = json.load(fh)

    public_key = content.pop('_public_key')
    private_key = load_private_key(public_key)

    enc_environment = content.pop('environment', {})
    enc_secrets = content.copy()

    return {
        'environment': decrypt_dict(enc_environment, private_key),
        **decrypt_dict(enc_secrets, private_key),
    }


def load_into_environ(path):
    env = load(path)['environment']
    os.environ.update(env)
