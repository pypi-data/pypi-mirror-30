# -*- coding: utf-8 -*-

"""
fwipy.compat
~~~~~~~~~~~~~~~

This module handles import compatibility issues between Python 2 and
Python 3.  (Thanks Kenneth and requests ✨🍰✨)
"""

import chardet

import sys

# -------
# Pythons
# -------

# Syntax sugar.
_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)


# ---------
# Specifics
# ---------

if is_py2:
    from urllib import (quote, unquote)

    builtin_str = str
    bytes = str
    str = unicode
    basestring = basestring
    numeric_types = (int, long, float)
    integer_types = (int, long)

elif is_py3:
    from urllib.parse import (quote, unquote)

    builtin_str = str
    str = str
    bytes = bytes
    basestring = (str, bytes)
    numeric_types = (int, float)
    integer_types = (int,)