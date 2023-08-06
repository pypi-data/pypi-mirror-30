# -*- coding: utf-8 -*-

import logging
import requests

from .compat import quote
from .fwi_base import Fwi

class ReaderId(Fwi):
    """Send a request to trigger a playtrigger inside of content player"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.url_schema = 'http://{0}:{1}/player/readerId/'.format(self.host, self.port)

        if self.debug:
            logging.debug('Url Schema: {0}'.format(url_schema))

    def trigger_id(self, id):
        """Accepts a readerId to send to content player, returns a requests response object"""
        url = self.url_schema + quote(str(id))

        resp = self._make_request(url)

        if self.debug:
            logging.debug('{0} triggered'.format(url))

        return {'id': id,
                'resp': resp}


