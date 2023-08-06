from __future__ import absolute_import, print_function, unicode_literals

import time

try:  # python2
    from functools32 import lru_cache
except ImportError:  # pragma: no cover python3
    from functools import lru_cache

from . import utils


class Client(utils.SecretKeyInterface):

    def __init__(self, client_id, secret_key=None, auth_type=None, timeout=300):
        self.id = client_id
        self.secret_key = secret_key
        self.auth_type = auth_type or 'SSR'
        self.timestamp = int(time.time())
        self.timeout = timeout

    @lru_cache(maxsize=1)
    def generate_pub_key(self, timestamp):
        assert self.secret_key is not None
        return utils.generate_public_key(self.id, timestamp, self.secret_key)

    def get_timestamp(self):
        now = int(time.time())
        if not 0 < now - self.timestamp <= self.timeout:
            self.timestamp = now
        return self.timestamp

    @property
    def headers(self):
        """Return a dictionary containing the headers to use in a request.

        Contains:
            client_id {string}
            timestamp {string}
            authorization {string}
        """
        timestamp = self.get_timestamp()
        return self.generate_headers(timestamp)

    @property
    def access_key(self):
        timestamp = self.get_timestamp()
        return '{}:{}:{}'.format(
            self.id,
            timestamp,
            self.generate_pub_key(timestamp)
        )

    def generate_headers(self, timestamp):
        pub_key = self.generate_pub_key(timestamp)
        return {
            'client_id': self.id,
            'timestamp': str(timestamp),
            'authorization': '{} {}'.format(self.auth_type, pub_key)
        }

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)

    def __str__(self):
        return self.id
