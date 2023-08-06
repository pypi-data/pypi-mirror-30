from __future__ import absolute_import, print_function, unicode_literals

from unittest import TestCase
try:
    from unittest import mock
except ImportError:
    import mock

from ssr.utils import SecretKeyInterface


class TestSecretKeyInterface(TestCase):

    def test_get_secret_key(self):
        interface = SecretKeyInterface()
        with mock.patch.object(interface, 'get_secret_key') as get_secret_key:
            secret_key = interface.secret_key
            self.assertEqual(secret_key, get_secret_key())
        self.assertIsNone(interface.get_secret_key())

    def test_secret_key_idempotence(self):
        interface = SecretKeyInterface()
        with mock.patch.object(interface, 'get_secret_key') as get_secret_key:
            interface.secret_key
            self.assertEqual(get_secret_key.call_count, 1)
            interface.secret_key
            self.assertEqual(get_secret_key.call_count, 1)

    def test_secret_key_setter(self):
        interface = SecretKeyInterface()
        with mock.patch.object(interface, 'get_secret_key') as get_secret_key:
            interface.secret_key = 'foo'
            self.assertEqual(interface.secret_key, 'foo')
            self.assertEqual(get_secret_key.call_count, 0)
