# ecfg

[![Version](https://img.shields.io/pypi/v/ecfg.svg)](https://pypi.python.org/pypi/ecfg)
[![License](https://img.shields.io/pypi/l/ecfg.svg)](https://pypi.python.org/pypi/ecfg)
[![PythonVersions](https://img.shields.io/pypi/pyversions/ecfg.svg)](https://pypi.python.org/pypi/ecfg)
[![Build](https://travis-ci.org/pior/ecfg.svg?branch=master)](https://travis-ci.org/pior/ecfg)

Python 3.5+ library to decrypt EJSON files.


## What is this?

[EJSON](https://github.com/Shopify/ejson) is a file format intended to store encrypted
secrets in project repository.
It uses an asymetric encryption ([NaCl Box](http://nacl.cr.yp.to/box.html)) to allow
any developer to add and update secrets while keeping the private key on servers.

This project relies on [PyNaCl](https://github.com/pyca/pynacl/) for the crypto.


## Features

Currently, only loading (decrypting) secrets from ejson files is supported.

More features (encrypt/cli) may be added if needed/requested.


## Usage

```shell
$ pip install ecfg
...
```

**Load/Decrypt a file:**

```python
import ecfg

secrets = ecfg.load('config/secrets.production.ejson')
secrets['database_url']
```

**Load the `environment` section directly into the process environment (`os.environ`)**:

```python
import ecfg

ecfg.load_into_environ('config/secrets.production.ejson')
```
