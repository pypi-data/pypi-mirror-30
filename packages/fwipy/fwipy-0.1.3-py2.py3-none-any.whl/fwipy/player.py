# -*- coding: utf-8 -*-

import logging
import requests

from .compat import quote
from .fwi_base import Fwi


class Player(Fwi):
    """wraps player commands"""

    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)

        self.url_schema = 'http://{0}:{1}/player/command/RunScript?1='.format(self.host,
                                                                              self.port)
        if self.debug:
            logging.debug('Url Schema: {0}'.format(self.url_schema))

    def set_variable(self, name, value):
        name = quote(str(name))
        value = quote(str(value))

        script_schema = 'Player.SetVariable({0}, "{1}");'.format(name, value)

        url = self.url_schema + script_schema
        resp = self._make_request(url)

        if self.debug:
            logging.debug('Script: {0}'.format(script_schema))

        return {'name': name,
                'value': value,
                'resp': resp}

    def play_content(self, name, value):
        name = quote(str(name))
        value = quote(str(value))

        script_schema = 'Template.PlayContent({0}, "{1}")'.format(name, value)

        url = self.url_schema + script_schema
        resp = self._make_request(url)

        if self.debug:
            logging.debug('Script: {0}'.format(script_schema))

        return {'name': name,
                'value': value,
                'resp': resp}

    def play_template(self, name):
        name = quote(name)

        script_schema = 'Player.PlayTemplate({0})'.format(name)

        url = self.url_schema + script_schema
        resp = self._make_request(url)

        if self.debug:
            logging.debug('Script: {0}'.format(script_schema))

        return {'name': name,
                'resp': resp}
