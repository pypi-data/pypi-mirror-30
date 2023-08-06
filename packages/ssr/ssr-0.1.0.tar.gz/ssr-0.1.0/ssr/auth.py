from __future__ import absolute_import, print_function, unicode_literals

import time
from .exceptions import AuthenticationError, TimeoutError
from . import utils


class BaseAuthentication(utils.SecretKeyInterface):

    auth_type = 'SSR'
    timeout = 300
    header_prefix = None
    access_key_name = 'key'

    def get_header_value(self, data, name, default=None):
        prefix = self.header_prefix or ''
        name = prefix + name
        return data.get(name.lower(), default)

    def validate_headers(self, data):
        cleaned_data = {key.lower(): value for key, value in data.items()}
        authorization = self.get_header_value(cleaned_data, 'authorization', '')
        if not authorization.startswith('{} '.format(self.auth_type)):
            return
        parts = authorization.split(' ')
        if len(parts) != 2:
            raise AuthenticationError('Invalid authorization.')
        _, pub_key = parts

        client_id = self.get_header_value(cleaned_data, 'client_id')
        timestamp = self.get_header_value(cleaned_data, 'timestamp', 0)
        return self.validate(client_id, timestamp, pub_key)

    def validate_access_key(self, access_key):
        try:
            client_id, timestamp, pub_key = access_key.split(':')
        except ValueError:
            raise AuthenticationError('Invalid access key.')
        return self.validate(client_id, timestamp, pub_key)

    def validate(self, client_id, timestamp, expected_key):
        """Return true if the header parts are valid.

        If not then AuthenticationError is raised.
        Check if timestamp exceeds a default 5 minute window.
        """
        current_timestamp = time.time()
        if not 0 <= (current_timestamp - int(timestamp)) <= self.timeout:
            raise TimeoutError('Invalid timestamp.')

        pub_key = utils.generate_public_key(client_id, timestamp, self.secret_key)
        if pub_key != expected_key:
            raise AuthenticationError('Invalid public key.')
        return True

    def get_params_value(self, request, name, default=None):
        params = self.get_params(request) or {}
        return params.get(name, default)

    def get_data_value(self, request, name, default=None):
        data = self.get_data(request) or {}
        return data.get(name, default)

    def get_headers(self, request):
        raise NotImplementedError()

    def get_params(self, request):
        raise NotImplementedError()

    def get_data(self, request):
        raise NotImplementedError()

    def get_access_key(self, request):
        return self.get_params_value(
            request,
            self.access_key_name,
            self.get_data_value(request, self.access_key_name)
        )

    def authenticate(self, request, *args, **kwargs):
        access_key = self.get_access_key(request)
        if access_key is None:
            headers = self.get_headers(request)
            authed = self.validate_headers(headers)
        else:
            authed = self.validate_access_key(access_key)
        return authed
