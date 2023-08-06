
fwipy - Python Wrapper for Content Player Socket Operations
===========================================================
.. image:: https://img.shields.io/pypi/v/fwipy.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/fwipy/
.. image:: https://img.shields.io/pypi/l/fwipy.svg?maxAge=2592000
    :target: https://opensource.org/licenses/Apache-2.0

Examples
--------
.. code-block:: python

    >>> from fwipy import Player

    >>> player = Player(host='127.0.0.1',
                port=10561,
                username='admin',
                password='fourwinds')

    >>> player.set_variable('foo', 'bar')




