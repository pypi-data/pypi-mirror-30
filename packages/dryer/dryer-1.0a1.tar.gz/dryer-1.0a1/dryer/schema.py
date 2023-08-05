"""
Schema
~~~~~~

Validates and coerce against a schema. There is 3 ways of defining a schema.

Subclassing::

    MySchema(Schema):
        fields = [
            field('foo'),
            field('bar')
        ]

At instantiation::

    schema = Schema(fields=[field('foo'), field('bar')])


Compose programmatically::

    schema = Schema()
    schema.add_field('foo')
    schema.add_field('bar')


By default it will fetch same obj attr than field name but can be hooked with
`lookup` and `lookup_cls`::

    obj = {'foo': 'by key'}
    obj.bar = 'by attr'

    schema = Schema()
    schema.add_field('foo', lookup=itemgetter('foo'))
    schema.add_field('bar')
    schema.add_field('len', lookup=methodcaller('__len__'))
    assert schema(obj) == {'foo': 'by key', 'bar': 'by attr': 'len': 1}

By default, field returns identity but they can coerce, compose object::

    schema = Schema()
    schema.add_field('value', lookup=attrgetter('foo'), type=str)
    schema.add_field('value_len', lookup=attrgetter('foo'), type=len)
    assert schema(obj) == {'value': 'by attr': 'value_len': 7}
"""

from .bases import Type, MemberTypeError
from .utils import reify
from operator import itemgetter, attrgetter, methodcaller
from functools import partial

__all__ = ['Field', 'Schema', 'schemamethod', 'itemgetter',
           'attrgetter', 'methodcaller', 'field']


def identity(obj):
    return obj


class Schema(Type):
    name = None
    fields: list = None
    lookup_cls: callable = None

    def __init__(self, name: str = None, fields: list = None, lookup_cls=None):
        self.name = name or type(self).name or self.__class__.__name__
        self.fields = type(self).fields or []
        self.fields.extend(fields or [])
        self.lookup_cls = lookup_cls or type(self).lookup_cls or attrgetter

    def add_field(self, *args, **kwargs) -> 'Field':
        field = Field(*args, **kwargs)
        self.fields.append(field)
        self.__dict__.pop('_bound', None)  # uncache bound fields
        return field

    @reify
    def _bound(self):
        sources = []
        for field in self.fields:
            sources.append(field._bind(self))
        return sources

    def __call__(self, obj) -> dict:
        elts = []
        errors = {}
        for key, coerce in self._bound:
            try:
                elts.append((key, coerce(obj)))
            except Exception as error:
                errors[key] = error
        if errors:
            raise MemberTypeError('error in schema %s' % self.name, obj, errors)
        return dict(elts)


class Field:
    """
    Parameters:
        name (str): name of destination field
        lookup (object): how to extract value from obj
        type (object): transformation applied to extracted value
        many (bool): value is a vector apply type to each member
        required (bool): lookup can fail or not
        default (object): fallback value when lookup failed
    """
    def __init__(self, name: str, lookup=None, *,
                 type=identity, many: bool = None, required: bool = True, default=None):
        """
        lookup is one of operator methodcaller, attrgetter, itemgetter. or if it's a str it will call schema method
        """
        self.name = name
        self.lookup = lookup
        self.type = type
        self.many = many
        self.required = required
        self.default = default

    def get_lookup(self, schema: 'Schema'):
        lookup = self.lookup
        if self.lookup is None:
            lookup = schema.lookup_cls
        if lookup in (attrgetter, itemgetter, methodcaller):
            lookup = lookup(self.name)
        elif lookup is schemamethod:
            lookup = lookup('get_%s' % self.name)
        elif isinstance(lookup, str):
            lookup = schemamethod(lookup)
        if hasattr(lookup, '_bind'):
            lookup = lookup._bind(schema)
        return lookup

    def _bind(self, schema: 'Schema'):
        lookup = self.get_lookup(schema)

        def caller(obj):
            try:
                value = lookup(obj)
            except (AttributeError, KeyError):
                if self.required:
                    raise
                value = self.default
            else:
                if self.many:
                    value = [self.type(elt) for elt in value]
                else:
                    value = self.type(value)
            return value
        return self.name, caller


def field(name: str, lookup=None, **kwargs) -> Field:
    if isinstance(lookup, attrgetter) and len(lookup._attrs) > 1:
        many = True
    elif isinstance(lookup, itemgetter) and len(lookup._items) > 1:
        many = True
    else:
        many = False
    kwargs.setdefault('many', many)

    return Field(name, lookup, **kwargs)


class schemamethod:
    """
    Return a callable object that calls the given method on its operand.
    After f = schemamethod('name'), the call f(schema, r) returns r.name().
    After g = schemamethod('name', 'date', foo=1), the call g(schema, r) returns
    r.name('date', foo=1).
    """

    def __init__(*args, **kwargs):
        try:
            self, name, *args = args
            assert isinstance(name, str)
        except (ValueError, AssertionError):
            raise TypeError("methodcaller needs at least one argument, the method name")
        self.name = name
        self.args = tuple(args)
        self.kwargs = kwargs

    def __call__(self, schema, obj):
        return getattr(schema, self.name)(obj, *self.args, **self.kwargs)

    def _bind(self, schema: 'Schema'):
        func = getattr(schema, self.name)
        args = self.args
        kwargs = self.kwargs
        return lambda obj: func(obj, *args, **kwargs)

    def __repr__(self):
        args = [repr(self.name)]
        args.extend(map(repr, self.args))
        args.extend('%s=%r' % (k, v) for k, v in self.kwargs.items())
        return '%s.%s(%s)' % (self.__class__.__module__,
                              self.__class__.__name__,
                              ', '.join(args))

    def __reduce__(self):  # pragma: no cover
        if not self.kwargs:
            return self.__class__, (self.name,) + self.args
        else:
            return partial(self.__class__, self.name, **self.kwargs), self.args
