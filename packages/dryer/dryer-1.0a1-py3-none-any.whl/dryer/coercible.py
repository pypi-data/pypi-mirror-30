"""
Coercible values
~~~~~~~~~~~~~~~~
"""

from .bases import Type, InvalidTypeError
from .utils import parse_rfc3339_date, parse_rfc3339_datetime, parse_rfc3339_time, ParseError
from datetime import date, time, datetime
from decimal import Decimal as decimal
from uuid import UUID as uuid

__all__ = [
    'Date',
    'DateTime',
    'Time',
    'UUID',
    'Integer',
    'Decimal',
    'Float',
    'Bool',
    'Null'
]


class Integer(Type):
    """Coerce integer alike to pure :class:`int`

    >>> assert Integer('12') == 12
    True
    >>> assert Integer(12.0) == 12
    True
    """

    def __call__(self, obj) -> int:
        try:
            if isinstance(obj, (bool, int, str)):
                return int(obj)
            if isinstance(obj, (decimal, float)):
                casted = int(obj)
                if casted == obj:
                    return casted
        except Exception as error:
            raise TypeError('Invalid integer value', obj) from error
        raise InvalidTypeError('Expected integer', type(obj))


class Decimal(Type):
    """Coerce number alike to pure :class:`decimal.Decimal`

    >>> assert Decimal('12') == decimal.Decimal('12')
    True
    """

    def __call__(self, obj) -> decimal:
        if not isinstance(obj, (int, str, float, decimal)):
            raise InvalidTypeError('Expected string', type(obj))
        try:
            return decimal(obj)
        except Exception as error:
            raise TypeError('Invalid decimal.Decimal', obj) from error


class Float(Type):
    """Coerce float alike to pure :class:`float`

    >>> assert Integer('12') == 12
    True
    >>> assert Integer(12.0) == 12
    True
    """

    def __call__(self, obj) -> float:
        if not isinstance(obj, (int, str, float, decimal)):
            raise InvalidTypeError('Expected float', type(obj))
        try:
            return float(obj)
        except ValueError as error:
            raise TypeError('Invalid float', obj) from error


class Bool(Type):
    """Coerce bool alike to pure :class:`bool`

    >>> assert Integer(1) is True
    True
    >>> assert Integer('on') is True
    True
    >>> assert Integer('true') is True
    True
    """

    def __call__(self, obj) -> bool:
        if obj in (0, 1, True, False):
            return bool(obj)
        if isinstance(obj, str):
            if str(obj).lower() in ('false', '0', 'off', 'no'):
                return False
            if str(obj).lower() in ('true', '1', 'on', 'yes'):
                return True
            raise TypeError('Invalid boolean', obj)
        raise InvalidTypeError('Expected bool', type(obj))


class Null(Type):
    """Coerce null alike to `None` value

    >>> assert Null('') is None
    True
    >>> assert Null(None) is None
    True
    """
    def __call__(self, obj) -> None:
        if obj in (None, ''):
            return None
        raise InvalidTypeError('Expected null', type(obj))


class Date(Type):
    """Coerce date alike to pure :class:`datetime.date`

    >>> assert Date('2018-12-23') == datetime.date(2018, 12, 23)
    True
    """

    def __call__(self, obj) -> date:
        if isinstance(obj, date):
            return obj
        if isinstance(obj, str):
            try:
                return parse_rfc3339_date(obj)
            except ParseError as error:
                raise TypeError('Invalid date string', obj) from error
        raise InvalidTypeError('Expected datetime.date', type(obj))


class DateTime(Type):
    """Coerce datetime alike to pure :class:`datetime.datetime`

    >>> assert DateTime('2018-12-23T12:23:34') == datetime.datetime(2018, 12, 23, 12, 23, 34)
    True
    """

    def __call__(self, obj) -> datetime:
        if isinstance(obj, datetime):
            return obj
        if isinstance(obj, str):
            try:
                return parse_rfc3339_datetime(obj)
            except ParseError as error:
                raise TypeError('Invalid datetime string', obj) from error
        raise InvalidTypeError('Expected datetime.datetime', type(obj))


class Time(Type):
    """Coerce date alike to pure :class:`datetime.time`

    >>> assert Time('12:23:34') == datetime.time(12, 23, 34)
    True
    """

    def __call__(self, obj) -> time:
        if isinstance(obj, time):
            return obj
        if isinstance(obj, str):
            try:
                return parse_rfc3339_time(obj)
            except ParseError as error:
                raise TypeError('Invalid time string', obj) from error
        raise InvalidTypeError('Expected datetime.time', type(obj))


class UUID(Type):
    """Coerce uuid alike to pure :class:`uuid.UUID`

    >>> assert UUID('3ae5b551-8767-4441-b68a-288a25f2de6c').__class__ is uuid.UUID
    True
    """

    def __call__(self, obj) -> uuid:
        if isinstance(obj, uuid):
            return obj
        if isinstance(obj, str):
            try:
                return uuid(obj)
            except ValueError as error:
                raise TypeError('Invalid uuid string', str(obj)) from error
        raise InvalidTypeError('Expected uuid.UUID', type(obj))


Date = Date()
DateTime = DateTime()
Time = Time()
UUID = UUID()
Integer = Integer()
Decimal = Decimal()
Float = Float()
Bool = Bool()
Null = Null()
