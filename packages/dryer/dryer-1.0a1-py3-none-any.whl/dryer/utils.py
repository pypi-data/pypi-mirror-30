import re
from datetime import datetime, date, time


def conv(num: int, b: int) -> str:
    """Convert number to base b. ~ inverse of int(num, b)
    """
    conv_str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    items = []
    while True:
        value = conv_str[num % b]
        items.append(value)
        num = num // b
        if num == 0:
            break
    return ''.join(sorted(items, reverse=True))


class ParseError(Exception):
    pass


DATE_PATTERN = re.compile('(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})')
TIME_PATTERN = re.compile('(?P<hours>\d{2}):(?P<minutes>\d{2})(:(?P<seconds>\d{2})(\.(?P<frac>\d+))?)?')


def parse_rfc3339_date(value: str) -> date:
    try:
        match = DATE_PATTERN.fullmatch(value)
        y, m, d = match.group('year', 'month', 'day')
        year = int(y)
        month = int(m)
        day = int(d)
        return date(year, month, day)
    except Exception as error:
        raise ParseError("%r is not a valid date" % value) from error


def parse_rfc3339_time(value: str) -> time:
    # TODO implement tzinfo
    # pass with hh:mm, hh:mm:ss, hh:mm:ss.s
    orig = value
    try:
        match = TIME_PATTERN.fullmatch(value)
        h, m, s, f = match.group('hours', 'minutes', 'seconds', 'frac')
        hours = int(h)
        minutes = int(m)
        seconds = int(s or '0')
        microseconds = 0

        if f and len(f) == 3:
            microseconds = int(f) * 1000
        elif f and len(f) == 6:
            microseconds = int(f)
        elif f:
            raise ValueError('cannot parse remaining %r' % f)

        return time(hour=hours,
                    minute=minutes,
                    second=seconds,
                    microsecond=microseconds)
    except Exception as error:
        raise ParseError("%r is not a valid time" % orig) from error


def parse_rfc3339_datetime(value: str) -> datetime:
    try:
        date_part, time_part = value.split('T')
        date = parse_rfc3339_date(date_part)
        time = parse_rfc3339_time(time_part)
        return datetime(year=date.year,
                        month=date.month,
                        day=date.day,
                        hour=time.hour,
                        minute=time.minute,
                        second=time.second,
                        microsecond=time.microsecond,
                        tzinfo=time.tzinfo)
    except Exception as error:
        raise ParseError("%r is not a valid datetime" % value) from error


class reify:
    '''Like property, but saves the underlying method's result for later use.

    Use as a class method decorator. It operates almost exactly like the Python
    ``@property`` decorator, but it puts the result of the method it decorates
    into the instance dict after the first call, effectively replacing the
    function it decorates with an instance variable. It is, in Python parlance,
    a non-data descriptor. An example:

    .. code-block:: python

       class Foo(object):
           @reify
           def jammy(self):
               print('jammy called')
               return 1

    And usage of Foo:

    >>> f = Foo()
    >>> v = f.jammy
    'jammy called'
    >>> print(v)
    1
    >>> f.jammy
    1
    >>> # jammy func not called the second time; it replaced itself with 1
    '''

    def __init__(self, func):
        try:
            self.__doc__ = func.__doc__
        except AttributeError:  # pragma: no cover
            pass
        self.func = func
        self.name = func.__name__

    def __get__(self, obj, cls):
        if obj is None:  # pragma: no cover
            return self
        try:
            value = obj.__dict__[self.name]
        except KeyError:
            value = obj.__dict__[self.name] = self.func(obj)
        return value

    def __set__(self, obj, value):  # pragma: no cover
        raise AttributeError("reified property is read-only")


# doc decorator
# took from https://gist.github.com/bfroehle/4041015

"""Property decorator for the `__doc__` attribute.
Useful for when you want a custom docstring for class instances
while still showing a generic docstring for the class itself.
A naive attempt using `@property` generally breaks Sphinx as
`cls.__doc__` returns the property object itself, and not a string.
See the documentation for `docstring_property` for an example.
"""


def docstring_property(class_doc):
    """Property attribute for docstrings.
    Usage
    -----
    >>> class A(object):
    ...     '''Main docstring'''
    ...     def __init__(self, x):
    ...         self.x = x
    ...     @docstring_property(__doc__)
    ...     def __doc__(self):
    ...         return "My value of x is %s." % self.x
    >>> A.__doc__
    'Main docstring'
    >>> a = A(10)
    >>> a.__doc__
    'My value of x is 10.'
    """
    def wrapper(fget):
        return DocstringProperty(class_doc, fget)
    return wrapper


class DocstringProperty(object):
    """Property for the `__doc__` attribute.
    Different than `property` in the following two ways:
    * When the attribute is accessed from the main class, it returns the value
      of `class_doc`, *not* the property itself. This is necessary so Sphinx
      and other documentation tools can access the class docstring.
    * Only supports getting the attribute; setting and deleting raise an
      `AttributeError`.
    """

    def __init__(self, class_doc, fget):
        self.class_doc = class_doc
        self.fget = fget

    def __get__(self, obj, type=None):
        if obj is None:
            return self.class_doc
        else:
            return self.fget(obj)

    def __set__(self, obj, value):
        raise AttributeError("can't set attribute")

    def __delete__(self, obj):
        raise AttributeError("can't delete attribute")
