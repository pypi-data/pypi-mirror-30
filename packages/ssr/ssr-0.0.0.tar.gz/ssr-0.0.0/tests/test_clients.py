from __future__ import absolute_import, print_function, unicode_literals

import time
import unittest
from ssr import random
from ssr.clients import AuthenticationError, Client


class UtilsTests(unittest.TestCase):

    def test_client_headers(self):
        client_id = '12345'
        client_access_key = '67890'
        client = Client(client_id, client_access_key)
        self.assertEqual(client.headers['Client'], client_id)
        self.assertTrue(client.headers['Authorization'].startswith(client.auth_type))

    def test_client_generate_pub_key(self):
        client = Client('id', random.secret())
        timestamp = int(time.time())
        key1 = client.generate_pub_key('id', timestamp)
        self.assertIsInstance(key1, str)
        key2 = client.generate_pub_key('id', timestamp)
        self.assertEqual(key1, key2)

    def test_client_validate_key(self):
        secret = random.secret()
        client = Client('id', secret)
        timestamp = int(time.time())
        key = client.generate_pub_key('id', timestamp)
        client2 = Client('diff_id', secret)
        self.assertTrue(
            client2.validate_key(client.client_id, timestamp, key)
        )

    def test_host_authenticate_invalid_timestamps(self):
        client = Client('id', 'secret')
        now = int(time.time())
        self.assertRaises(
            AuthenticationError,
            client.authenticate,
            'client_id',
            now + 1000,
            'SSR authorization',
        )
        self.assertRaises(
            AuthenticationError,
            client.authenticate,
            'client_id',
            now - 1000,
            'SSR authorization',
        )

    def test_client_authenticate_invalid_authorization_type(self):
        client = Client('id', 'secret')
        now = time.time()
        self.assertIsNone(
            client.authenticate(
                'client_id',
                now,
                'bad',
            )
        )
        self.assertIsNone(
            client.authenticate(
                'client_id',
                now,
                'bad authorization',
            )
        )

    def test_client_registry_and_authentication(self):
        client = Client(random.client_id(), random.secret())
        headers = client.headers
        self.assertTrue(
            client.authenticate(
                headers['Client'],
                headers['Timestamp'],
                headers['Authorization'],
            )
        )
        now = time.time()
        self.assertRaises(
            AuthenticationError,
            client.authenticate,
            client.client_id,
            now,
            'SSR badtoken',
        )

    def test_client_queryparams(self):
        client = Client('id', random.secret())
        self.assertIsInstance(client.queryparams, str)
