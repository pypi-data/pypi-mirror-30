# -*- coding: utf-8 -*-

import logging
import requests

from .compat import quote
from .fwi_base import Fwi


class Template(Fwi):
    """wraps template commands"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.url_schema = 'http://{0}:{1}/player/command/RunScript?1='.format(self.host,
                                                                            self.port)
        if self.debug:
            logging.debug('Url Schema: {0}'.format(url_schema))

    def play_content(self, name, value):
        name = quote(str(name))
        value = quote(str(value))

        script_schema = 'Template.PlayContent({0}, "{1}")'.format(name, value)

        url = url_schema + script_schema
        resp = self._make_request(url)

        if self.debug:
            logging.debug('Script: {0}'.format(script_schema))

        return {'name': name,
                'value': value,
                'resp': resp}
