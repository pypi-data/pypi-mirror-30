Dryer
=====

Coerce and serialize datastructures.


Usage
-----

Installation::

    python -m pip install dryer

There is some collections of types:

* Strict: validate strict object::

    from dryer import strict
    assert strict.String('a string') is str

* Coercible: coerce objects to expected result::

    from dryer import coercible
    assert coercible.Bool('true') is bool

* Json: coerce json values to Python object::

    import time
    from dryer import json
    assert json.Date('2018-12-23') is time.date


There is also a Schema lib that can serialize any structure to a simplified one:
