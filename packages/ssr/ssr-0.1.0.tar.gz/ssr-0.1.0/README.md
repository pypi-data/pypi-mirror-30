# ssr

Shared-Secret Requests: A simple HTTP authentication library using shared secrets.

## Overview

The `ssr` library exposes a simple set interfaces that facilitate server-server
authentication using a shared secret. This shared secret or `secret_key` is used
to generate a public key, using a client id and timestamp. The combination of the
client id, timestamp and public key form a signature that a host server can use
to verify the identity of the client server.

## Scope

The scope of this project is limited to inter-app authentication e.g. to support RESTful
data transfer between micro-services. Logistics around managing secrets is noot included
in the scope of this project. For tools to manage secrets you can look into:

* [ansible-vault](https://github.com/tomoh1r/ansible-vault)
* [kms-vault](https://github.com/hangarunderground/kms-vault)

## Installation

`pip install ssr`

## Usage

### SSR Client

TBD

### Requests Session

```python
import ssr

session = ssr.Session(
    secret_key=os.environ.get('APP_SECRET_KEY')
)

response = session.get(
    'https://myblog.com/api/post_reports/',
    params={'q': 'auth'}
)
```

### Base Authentication

TBD
