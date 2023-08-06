from __future__ import absolute_import, print_function, unicode_literals

import hashlib


def generate_public_key(client_id, timestamp, secret_key):
    """Generate a SHA256 encoded hash using the client id, timestamp and secret key.

    Return the string public key.
    """
    key = '{}{}{}'.format(client_id, secret_key, timestamp)
    return hashlib.sha256(key.encode('utf-8')).hexdigest()


class SecretKeyInterface(object):

    _secret_key = None

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
