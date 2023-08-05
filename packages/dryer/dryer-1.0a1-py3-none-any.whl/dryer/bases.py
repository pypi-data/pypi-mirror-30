from .utils import docstring_property
from collections import abc

__all__ = ['Type', 'InvalidTypeError',
           'Union', 'UnionTypeError',
           'Vector', 'Mapping', 'MemberTypeError']


class Type:
    """Base of each type.

    Call be combined with other Type. For example:

    >>> NullableString = String | Null
    >>> assert NullableString('foo') == 'foo
    >>> assert NullableString(None) is None
    """

    def __or__(self, other: 'Type') -> 'Union':
        bases = other.bases if isinstance(other, Union) else (other,)
        return Union(self, *bases)

    def __call__(self, obj):  # pragma: no cover
        return obj

    def __repr__(self):
        return r(self)


class InvalidTypeError(TypeError):
    """Thrown on failure validation.

    Parameters:
        message (str): message of the failure
        reason (object): source of error
    """
    def __init__(self, message, reason):
        self.message = message
        self.reason = reason
        super().__init__(message, reason)


class Union(Type):
    """Implements a union type, aka:

    >>> type = Union(str, int)
    >>> assert type('foo').__class__ is str
    >>> assert type(12).__class__ is int
    >>> assert type(12.).__class__ is int

    Raises a :class:`UnionTypeError` if no match where found.
    """

    bases: tuple

    def __init__(self, *bases):
        assert bases
        self.bases = bases

    @docstring_property(__doc__)
    def __doc__(self):
        *heads, tail = [s(b) for b in self.bases]
        if heads:
            doc = "Expects one of %s or %s" % (', '.join(heads), tail)
        else:
            doc = "Expects a %s" % tail
        return doc

    def __or__(self, other: 'Type') -> 'Union':
        bases = other.bases if isinstance(other, Union) else (other,)
        cls = type(self)
        return cls(*self.bases, *bases)

    def __call__(self, obj):
        """In case of multiple alternatives, try to returns the exact same.
        otherwise return the first found.
        """
        alts: list = []
        errors: list = []
        for base in self.bases:
            try:
                value = base(obj)
                if value is obj:
                    return value
                alts.append(value)
            except Exception as error:
                errors.append(error)
        if alts:
            return alts[0]
        raise UnionTypeError('No match', obj, errors)

    def __repr__(self):
        query = ' | '.join(r(f) for f in self.bases)
        return '(%s)' % query


class UnionTypeError(TypeError):
    """Raised by :class:`Union`.

    One error from errors must be resolved to pass.
    """
    def __init__(self, message, obj, errors: list):
        self.message = message
        self.obj = obj
        self.errors = errors
        super().__init__(message, obj, errors)


class Vector(Type):
    """Allow to validate repeatably a vector (list, set or tuple)
    """

    base: object

    def __init__(self, base):
        self.base = base

    @docstring_property(__doc__)
    def __doc__(self):
        return "Expects a serie of %s." % s(self.base)

    def __call__(self, obj):
        if not isinstance(obj, (list, set, tuple)):
            raise InvalidTypeError('Expected vector', type(obj))
        coerce = self.base.__call__
        elts = []
        errors = {}
        for i, elt in enumerate(obj):
            try:
                elts.append(coerce(elt))
            except Exception as error:
                errors[i] = error
        if errors:
            raise MemberTypeError('error in vector', obj, errors)
        return obj.__class__(elts)

    def __repr__(self):
        return "[%s]" % r(self.base)


class Mapping(Type):
    """Allow to validate repeatably a mapping of same types
    """

    def __init__(self, base):
        self.base = base

    @docstring_property(__doc__)
    def __doc__(self):
        return "Expects a serie of %s." % s(self.base)

    def __call__(self, obj):
        if not isinstance(obj, dict):
            raise InvalidTypeError('Expected mapping', type(obj))
        coerce = self.base.__call__
        elts = []
        errors = {}
        for key, elt in obj.items():
            try:
                elts.append((key, coerce(elt)))
            except Exception as error:
                errors[key] = error
        if errors:
            raise MemberTypeError('error in mapping', obj, errors)
        return obj.__class__(elts)

    def __repr__(self):
        return "{%s}" % r(self.base)


class MemberTypeError(TypeError, abc.Mapping):
    """Raised by types that have erroneous members, like :class:`Vector`.

    Member errors can be accessed like a dict, for example:

    >>> error = MemberTypeError('', None, {'member': 'that error'})
    >>> assert error['member'] == 'that error'

    Parameters:
        message (str): the error message
        obj (object): the original object
        errors (dict): the mapping of erroneous members
    """

    def __init__(self, message, obj, errors):
        self.message = message
        self.obj = obj
        self.errors = errors
        super().__init__(message, obj, errors)

    def __getitem__(self, key):
        return self.errors[key]

    def __iter__(self):
        return iter(self.errors)

    def __len__(self):
        return len(self.errors)


def s(t):
    return f":class:`{r(t)}`"


def r(t):
    if not isinstance(t, type):
        t = t.__class__
    if t in (str, list, tuple, set, dict):
        return t.__qualname__
    return f"{t.__module__}.{t.__qualname__}"
