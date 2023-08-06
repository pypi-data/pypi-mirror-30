# Shared-Secret Requests (SSR)

[![CircleCI](https://circleci.com/gh/hangarunderground/ssr.svg?style=svg)](https://circleci.com/gh/hangarunderground/ssr)

[![codecov](https://codecov.io/gh/hangarunderground/ssr/graph/badge.svg)](https://codecov.io/gh/hangarunderground/ssr)

A simple HTTP authentication library using shared secrets.

## Overview

The `ssr` library exposes a simple set of interfaces that facilitate server-server
authentication using a shared secret. This shared secret or `secret_key` is used
to generate a public key, using a client id and timestamp. The combination of the
client id, timestamp and public key form a signature that a host server can use
to verify the identity of the client server. `ssr` provides 3 intefaces to support
that authentication workflow:

1. `ssr.Client` - to help generate a public key from a shared secret key.
2. `ssr.Session` - exends the `requests` library `Session` class to expose an `ssr.Client` and patch requests with the appropriate headers to correcly interface with `ssr.BaseAuthentication`
3. `ssr.BaseAuthentication` - to help hosts validate requests from clients that have the same shared secret.

## Scope

The scope of this project is limited to server-server authentication e.g. to support RESTful data transfer between micro-services. Logistics around managing secrets is not included in the scope of this project. For tools to manage secrets you can look into:

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


## TODO
