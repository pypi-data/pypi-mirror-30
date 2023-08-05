"""
Strict
~~~~~~

All object means to be strictly the same type as expected. For example:

>>> assert String('foo') == 'foo'

Will work, but this one will fail:

>>> String(12)
Traceback (most recent call last):
    ...
dryer.InvalidTypeError: ('Expected string', <class 'int'>)

"""

from .bases import Type, InvalidTypeError
from datetime import date, time, datetime
from decimal import Decimal as decimal
from uuid import UUID as uuid

__all__ = ['Null', 'String', 'UUID',
           'Integer', 'Float', 'Decimal', 'Number', 'Bool',
           'Date', 'Time', 'DateTime']


class Null(Type):
    """Expects a None value
    """

    def __call__(self, obj) -> None:
        """Expects a `None` value
        """
        if obj is not None:
            raise TypeError('Expected null', type(obj))
        return obj


class String(Type):
    """Expects a `str` value
    """

    def __call__(self, obj) -> str:
        if not isinstance(obj, str):
            raise InvalidTypeError('Expected string', type(obj))
        return obj


class Integer(Type):
    """Expects a strict `int` value, boolean will throw a TypeError.
    """

    def __call__(self, obj) -> int:
        if not isinstance(obj, int) or obj in (True, False):
            raise InvalidTypeError('Expected int', type(obj))
        return obj


class Bool(Type):
    """Expects a strict `bool` value, integer will throw a TypeError.
    """

    def __call__(self, obj) -> bool:
        if not isinstance(obj, bool):
            raise InvalidTypeError('Expected bool', type(obj))
        return obj


class Float(Type):
    """Expects a strict `float` value, other number value will throw a TypeError.
    """

    def __call__(self, obj) -> float:
        if not isinstance(obj, float):
            raise InvalidTypeError('Expected float', type(obj))
        return obj


class Decimal(Type):
    """Expects a strict `decimal.Decimal` value, other number value will throw a TypeError.
    """

    def __call__(self, obj) -> decimal:
        if not isinstance(obj, decimal):
            raise InvalidTypeError('Expected decimal.Decimal', type(obj))
        return obj


class Date(Type):
    """Expects a strict `datetime.date` value.
    """

    def __call__(self, obj) -> date:
        if not isinstance(obj, date):
            raise TypeError('Expected datetime.date', type(obj))
        return obj


class Time(Type):
    """Expects a strict `datetime.time` value.
    """

    def __call__(self, obj) -> time:
        if not isinstance(obj, time):
            raise TypeError('Expected datetime.time', type(obj))
        return obj


class DateTime(Type):
    """Expects a strict `datetime.datetime` value.
    """

    def __call__(self, obj) -> datetime:
        if not isinstance(obj, datetime):
            raise TypeError('Expected datetime.datetime', type(obj))
        return obj


class UUID(Type):
    """Expects a strict `uuid.UUID` value.
    """

    def __call__(self, obj) -> uuid:
        if not isinstance(obj, uuid):
            raise TypeError('Expected uuid.UUID', type(obj))
        return obj


Null = Null()
String = String()
UUID = UUID()
Integer = Integer()
Float = Float()
Decimal = Decimal()
Number = Integer | Float | Decimal
Bool = Bool()
Date = Date()
Time = Time()
DateTime = DateTime()
