from __future__ import absolute_import, print_function, unicode_literals

import time
import unittest
from ssr import random
from ssr import Client


class ClientTests(unittest.TestCase):

    def test_client_headers(self):
        client_id = '12345'
        secret_key = '67890'
        client = Client(client_id, secret_key)
        self.assertEqual(client.headers['client_id'], client_id)
        self.assertTrue(client.headers['authorization'].startswith(client.auth_type))

    def test_client_generate_pub_key(self):
        client = Client('id', random.secret())
        timestamp = int(time.time())
        key1 = client.generate_pub_key(timestamp)
        self.assertIsInstance(key1, str)
        key2 = client.generate_pub_key(timestamp)
        self.assertEqual(key1, key2)

    def test_repr(self):
        client = Client('bar', 'foo')
        self.assertEqual(repr(client), '<Client: bar>')
