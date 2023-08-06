from __future__ import absolute_import, print_function, unicode_literals


import requests
from . import random
from .clients import Client


class Session(requests.Session):

    def __init__(
        self,
        secret_key=None,
        auth_type=None,
        auth_timeout=None,
        *args,
        **kwargs
    ):
        super(Session, self).__init__(*args, **kwargs)
        self.ssr_client = self.get_ssr_client(
            secret_key,
            auth_type=auth_type,
            timeout=auth_timeout
        )

    def get_ssr_client(self, secret_key, auth_type=None, timeout=None):
        client_id = random.client_id()
        return Client(
            client_id,
            secret_key,
            auth_type=auth_type,
            timeout=timeout
        )

    @property
    def access_key(self):
        return self.ssr_client.access_key

    def request(self, *args, **kwargs):
        self.headers.update(self.ssr_client.headers)
        return super(Session, self).request(*args, **kwargs)
