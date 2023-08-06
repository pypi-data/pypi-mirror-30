# -*- coding: utf-8 -*-

#    ___        _ ___
#   | __|_ __ _(_) _ \_  _
#   | _|\ V  V / |  _/ || |
#   |_|  \_/\_/|_|_|  \_, |
#                     |__/

"""
Fwipy - Python Wrapper for Content Player Socket Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    >>> from fwipy import Player

    >>> player = Player(host='127.0.0.1',
                port=10561,
                username='admin',
                password='fourwinds')

    >>> player.set_variable('foo', 'bar')

:copyright: (c) 2017 by Erin O'Connell.
:license: Apache 2.0, see LICENSE for more details.
"""

from .player import Player
from .readerId import ReaderId
from .template import Template