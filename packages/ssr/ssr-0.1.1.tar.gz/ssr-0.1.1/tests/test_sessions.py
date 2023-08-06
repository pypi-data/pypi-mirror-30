from __future__ import absolute_import, print_function, unicode_literals

import responses

from unittest import TestCase
from ssr import random
from ssr.sessions import Session

try:
    from unittest import mock
except ImportError:
    import mock


class SessionTests(TestCase):

    def setUp(self):
        self.timeout = 1000
        self.session = Session(
            secret_key=random.secret(),
            auth_type='Test',
            auth_timeout=self.timeout
        )

    def test_access_key(self):
        self.assertEqual(
            self.session.access_key,
            self.session.ssr_client.access_key
        )

    def test_timeout(self):
        self.assertEqual(self.session.ssr_client.timeout, self.timeout)

    @responses.activate
    def test_request(self):
        with mock.patch('ssr.sessions.Client.generate_headers') as generate_headers:
            generate_headers.return_value = {'foo': 'bar'}
            responses.add(responses.GET, 'https://httpbin.org/anything')
            self.session.get('https://httpbin.org/anything')
            self.assertTrue(generate_headers.called)
