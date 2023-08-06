from __future__ import absolute_import, print_function, unicode_literals

import string

try:  # python2
    from random import SystemRandom

    def choice(chars):
        return SystemRandom().choice(chars)

except ImportError:  # pragma: no cover python3
    from secrets import choice


def random_string(chars, length):
    return ''.join([choice(chars) for _ in range(length)])


def secret(length=64):
    return random_string(string.digits + string.ascii_letters, length)


def client_id(length=8):
    return random_string(string.digits, length)
