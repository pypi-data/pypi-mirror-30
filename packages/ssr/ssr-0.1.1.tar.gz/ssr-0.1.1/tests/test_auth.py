from __future__ import absolute_import, print_function, unicode_literals

import os
import time
import unittest
from ssr import BaseAuthentication, random, utils
from ssr.exceptions import AuthenticationError

try:
    import mock
except ImportError:
    from unittest import mock


class ExampleAuthentication(BaseAuthentication):

    def __init__(self):
        self.secret_key = os.environ.get('APP_SECRET_KEY')

    def get_headers(self, request):
        return request.headers

    def get_params(self, request):
        return request.params

    def get_data(self, request):
        return request.data


class AuthenticationTests(unittest.TestCase):

    def setUp(self):
        self.timestamp = int(time.time())
        self.client_id = random.client_id()
        self.secret_key = os.environ.get('APP_SECRET_KEY', random.secret())

        os.environ.setdefault('APP_SECRET_KEY', self.secret_key)
        self.auth = ExampleAuthentication()
        self.request = mock.MagicMock()
        self.request.params = {}
        self.request.data = {}
        self.request.headers = {}

    def prep_headers(self, **kwargs):
        parts = self.valid_parts()
        parts['authorization'] = '{} {}'.format(
            self.auth.auth_type,
            parts['pub_key']
        )
        parts.update(kwargs)
        self.request.headers.update(parts)

    def valid_parts(self):
        return {
            'client_id': self.client_id,
            'timestamp': self.timestamp,
            'pub_key': utils.generate_public_key(
                self.client_id,
                self.timestamp,
                self.secret_key
            )
        }

    def valid_access_token(self):
        return '{client_id}:{timestamp}:{pub_key}'.format(**self.valid_parts())

    def test_authenticate_invalid_timestamps(self):
        now = int(time.time())
        self.prep_headers(timestamp=now + 1000)
        self.assertRaises(
            AuthenticationError,
            self.auth.authenticate,
            self.request
        )
        self.prep_headers(timestamp=now - 1000)
        self.assertRaises(
            AuthenticationError,
            self.auth.authenticate,
            self.request
        )

    def test_authenticate_invalid_authorization_type(self):
        self.prep_headers(authorization='bad')
        self.assertIsNone(self.auth.authenticate(self.request))

    def test_successful_authentication(self):
        self.prep_headers()
        self.assertTrue(self.auth.authenticate(self.request)[0])

    def test_invalid_pub_key(self):
        self.prep_headers(authorization='SSR badtoken')
        self.assertRaises(
            AuthenticationError,
            self.auth.authenticate,
            self.request
        )

    def test_invalid_pub_key_too_many_parts(self):
        self.prep_headers(authorization='SSR bad token')
        self.assertRaises(
            AuthenticationError,
            self.auth.authenticate,
            self.request
        )

    def test_valid_access_token(self):
        access_key = '{client_id}:{timestamp}:{pub_key}'.format(
            **self.valid_parts()
        )
        self.request.params['key'] = access_key
        self.assertTrue(self.auth.authenticate(self.request)[0])

    def test_invalid_access_token(self):
        access_key = 'foo'
        self.request.params['key'] = access_key
        self.assertRaises(
            AuthenticationError,
            self.auth.authenticate,
            self.request
        )

    def test_base_authentication_get_headers(self):
        self.assertRaises(
            NotImplementedError,
            BaseAuthentication().get_headers,
            self.request
        )

    def test_base_authentication_get_params(self):
        self.assertRaises(
            NotImplementedError,
            BaseAuthentication().get_params,
            self.request
        )

    def test_base_authentication_get_data(self):
        self.assertRaises(
            NotImplementedError,
            BaseAuthentication().get_data,
            self.request
        )

    def test_authenticate_header(self):
        self.assertIsNone(
            BaseAuthentication().authenticate_header(self.request)
        )
