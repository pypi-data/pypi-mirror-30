"""
JSON Objects
~~~~~~~~~~~~
"""

from .bases import Type, InvalidTypeError
from .utils import parse_rfc3339_date, parse_rfc3339_datetime, parse_rfc3339_time, ParseError
from datetime import date, time, datetime
from decimal import Decimal as decimal
from functools import singledispatch
from json import JSONEncoder as JSONEncoderBase
from uuid import UUID as uuid

__all__ = ['Null', 'String', 'UUID',
           'Integer', 'Float', 'Bool', 'Decimal',
           'Date', 'Time', 'DateTime', 'coerce', 'JSONEncoder']


class Null(Type):
    """Ensure value is strictly `None`.

    >>> assert Null(None) is None
    True
    """

    def __call__(self, obj) -> None:
        if obj is not None:
            raise TypeError('Expected null', type(obj))
        return obj


class String(Type):
    """Ensure value is str.

    >>> assert String('foo') is str
    True
    """
    def __call__(self, obj) -> str:
        if isinstance(obj, str):
            return str(obj)
        raise InvalidTypeError('Expected string', type(obj))


class Integer(Type):
    """Ensure value is strictly an `int`.

    >>> assert Integer(12) is int
    True
    """
    def __call__(self, obj) -> int:
        if isinstance(obj, int) and not isinstance(obj, bool):
            return int(obj)
        raise InvalidTypeError('Expected int', type(obj))


class Float(Type):
    """Ensure value is strictly a `float`.

    >>> assert Float(12.) is float
    True
    """
    def __call__(self, obj) -> float:
        if isinstance(obj, float):
            return float(obj)
        raise InvalidTypeError('Expected float', type(obj))


class Bool(Type):
    """Ensure value is strictly a `bool`.

    >>> assert Bool(True) is bool
    True
    """
    def __call__(self, obj) -> bool:
        if isinstance(obj, bool):
            return bool(obj)
        raise InvalidTypeError('Expected bool', type(obj))


class Decimal(Type):
    """Coerce number value to :class:`decimal.Decimal`.
    This is useful for `Infinity` and `NaN` values.

    >>> assert Decimal('Infinity') is decimal.Decimal
    True
    """
    def __call__(self, obj) -> decimal:
        if not isinstance(obj, str):
            raise InvalidTypeError('Expected str', type(obj))
        try:
            return decimal(obj)
        except Exception as error:
            raise TypeError('Invalid decimal.Decimal string', obj) from error


class Date(Type):
    """Coerce date string value to :class:`datetime.date`.

    >>> assert Date('2018-12-23') is datetime.date
    True
    """
    def __call__(self, obj) -> date:
        if not isinstance(obj, str):
            raise InvalidTypeError('Expected string', type(obj))
        try:
            return parse_rfc3339_date(obj)
        except ParseError as error:
            raise TypeError('Invalid date string', str(obj)) from error


class DateTime(Type):
    """Coerce datetime string value to :class:`datetime.datetime`.

    >>> assert DateTime('2018-12-23T12:23:34') is datetime.datetime
    True
    """
    def __call__(self, obj) -> datetime:
        if not isinstance(obj, str):
            raise InvalidTypeError('Expected string', type(obj))
        try:
            return parse_rfc3339_datetime(obj)
        except ParseError as error:
            raise TypeError('Invalid datetime string', str(obj)) from error


class Time(Type):
    """Coerce time string value to :class:`datetime.time`.

    >>> assert Time('12:23:34') is datetime.time
    True
    """
    def __call__(self, obj) -> time:
        if not isinstance(obj, str):
            raise InvalidTypeError('Expected string', type(obj))
        try:
            return parse_rfc3339_time(obj)
        except ParseError as error:
            raise TypeError('Invalid time string', str(obj)) from error


class UUID(Type):
    """Coerce uuid string value to :class:`uuid.UUID`.

    >>> assert Time('3ae5b551-8767-4441-b68a-288a25f2de6c') is uuid.UUID
    True
    """
    def __call__(self, obj) -> uuid:
        if not isinstance(obj, str):
            raise InvalidTypeError('Expected string', type(obj))
        try:
            return uuid(obj)
        except ValueError as error:
            raise TypeError('Invalid uuid string', str(obj)) from error


String = String()
Integer = Integer()
Float = Float()
Decimal = Decimal()
Number = Integer | Float | Decimal
Bool = Bool()
Null = Null()
Date = Date()
DateTime = DateTime()
Time = Time()
UUID = UUID()


@singledispatch
def coerce(obj):
    """Coerce python object to json representation.

    For example::

        obj = uuid.UUID('3ae5b551-8767-4441-b68a-288a25f2de6c')
        assert coerce(obj) == '3ae5b551-8767-4441-b68a-288a25f2de6c'
    """
    raise TypeError(repr(obj) + " cannot be coerced")


@coerce.register(dict)
def coerce_mapping(obj):
    return dict(obj)


@coerce.register(set)
@coerce.register(list)
@coerce.register(tuple)
def coerce_sequence(obj):
    return list(obj)


@coerce.register(date)
def coerce_date(obj):
    return obj.isoformat()


@coerce.register(time)
def coerce_time(obj):
    return obj.isoformat()


@coerce.register(datetime)
def coerce_datetime(obj):
    return obj.isoformat('T')


@coerce.register(uuid)
def coerce_uuid(obj):
    return str(obj)


@coerce.register(decimal)
def coerce_decimal(obj):
    return str(obj)


class JSONEncoder(JSONEncoderBase):
    """Custom version of standard json.JSONEncoder.
    """

    def default(self, obj):
        """Coerce values to json representation

        Can be used like this:

        >>> import json
        >>> json.dumps(datetime.date(2018, 12, 23), cls=JSONEncoder)
        '2018-12-23'
        """
        return coerce(obj)
