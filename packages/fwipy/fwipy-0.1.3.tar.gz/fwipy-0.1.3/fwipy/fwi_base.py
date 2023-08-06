# -*- coding: utf-8 -*-

import logging
import requests

from requests.auth import HTTPBasicAuth

class Fwi(object):
    """Base class for all fwi objects"""

    def __init__(self, **kwargs):
        self.host = kwargs.get('host', '127.0.0.1')
        self.debug = kwargs.get('debug')
        self.port = str(kwargs.get('port', '10561'))
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')

    def _make_request(self, payload):
        resp = requests.get(payload, auth=HTTPBasicAuth(self.username, self.password))
        return resp