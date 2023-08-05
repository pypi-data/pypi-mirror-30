# pylama: ignore=W0401,W0611

"""
This library offers composable class and functions for validating and coercing datastructure and objects.

For example, you expect that value is a strict :class:`str`:

>>> from dryer import strict
>>> strict.String('foo')
'foo'

Other object types will raise a :class:`TypeError`, for example:

>>> strict.String(12)
Traceback (most recent call last):
    ...
dryer.InvalidTypeError: ('Expected string', <class 'int'>)

"""

from .bases import *
from .schema import Schema
from . import coercible
from . import json
from . import schema
from . import strict
from ._version import get_versions

__all__ = bases.__all__ + ['Schema']
__version__ = get_versions()['version']
del get_versions
