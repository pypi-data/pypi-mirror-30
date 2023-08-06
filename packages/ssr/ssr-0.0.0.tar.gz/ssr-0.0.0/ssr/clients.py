from __future__ import absolute_import, print_function, unicode_literals

import hashlib
import time

from .exceptions import AuthenticationError

try:  # python2
    from functools32 import lru_cache
    from urllib import urlencode
except ImportError:  # pragma: no cover python3
    from functools import lru_cache
    from urllib.parse import urlencode


class Client(object):

    _secret_key = None

    def __init__(self, client_id, secret_key=None, auth_type=None, timeout=300):
        self.client_id = client_id
        self.secret_key = secret_key
        self.auth_type = auth_type or 'SSR'
        self.timestamp = int(time.time())
        self.timeout = timeout

    @property
    def secret_key(self):
        if self._secret_key is None:
            self._secret_key = self.get_secret_key()
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

    def get_secret_key(self):
        """Override or set secret_key."""
        pass

    def generate_pub_key(self, client_id, timestamp):
        """Generate a SHA256 encoded hash using the client id, timestamp and secret key.

        Return the string public key.
        """
        assert self.secret_key is not None
        key = '{}{}{}'.format(client_id, self.secret_key, timestamp)
        return hashlib.sha256(key.encode('utf-8')).hexdigest()

    def get_timestamp(self):
        now = int(time.time())
        if not 0 < now - self.timestamp <= self.timeout:
            self.timestamp = now
        return self.timestamp

    @property
    def headers(self):
        """Return a dictionary containing the headers to use in a request.

        Contains:
            Client {string}
            Timestamp {string}
            Authorization {string}
        """
        timestamp = self.get_timestamp()
        return self.generate_headers(timestamp)

    @lru_cache(maxsize=1)
    def generate_headers(self, timestamp):
        pub_key = self.generate_pub_key(self.client_id, timestamp)
        return {
            'Client': self.client_id,
            'Timestamp': str(timestamp),
            'Authorization': '{} {}'.format(self.auth_type, pub_key)
        }

    @property
    def queryparams(self):
        """URL encodes the client's headers."""
        return urlencode({
            k.lower(): v
            for k, v in self.headers.items()
        })

    def validate_key(self, client_id, timestamp, expected_key):
        """Validate the token passed in the request.

        This is checked against the client id and timestamp used for authentication.
        Returns true if the information used to generate the public key with the local
        secret matches the expected key.
        """
        pub_key = self.generate_pub_key(client_id, timestamp)
        return pub_key == expected_key

    def authenticate(self, client_id, timestamp, authorization):
        """Return true if the header parts are valid.

        If not then AuthenticationError is raised.
        Check if timestamp exceeds a default 5 minute window.
        """
        if not authorization.startswith('{} '.format(self.auth_type)):
            return

        current_timestamp = time.time()
        if not 0 <= (current_timestamp - int(timestamp)) <= self.timeout:
            raise AuthenticationError('Invalid timestamp')

        parts = authorization.split(' ')
        if len(parts) != 2:
            raise AuthenticationError('Invalid credentials')
        _, pub_key = parts

        if not self.validate_key(client_id, timestamp, pub_key):
            raise AuthenticationError('Invalid authorization token')
        return True

    def __hash__(self):
        return hash(self.client_id)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)

    def __str__(self):
        return self.client_id
