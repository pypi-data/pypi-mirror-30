============
 voluptuary
============

This is a tool and library to convert a JSON Schema to a Voluptuous schema.

Usage
-----

.. code-block:: python

    from voluptuary import to_voluptuous

    # some JSON Schema
    json_schema = {
        'type': 'object',
        'properties': {
            'value': {'type': 'integer'},
        },
    }

    # convert to a voluptuous schema
    schema = to_voluptuous(json_schema)

    # validate something
    schema({'value': 1})

Tests
-----

To run the tests, use `tox`_.

.. code-block:: bash

    $ tox

Why?
----

This library is for the people who aren't satisfied with JSON Schema but can't
justify rewriting schemas ("tedious", "time-consuming", "little benefit"). But
with a library to rewrite the schemas for you, there are no more excuses!

If you are wondering "why voluptuous over JSON Schema", there are some good
`reasons listed here`_. I find voluptuous models to be nicer: more Pythonic,
more expressive, easier to read and maintain, easier to customize, better error
messages, and so on.

How do I know my converted schema will validate correctly?
----------------------------------------------------------

First of all, you should always test the validation behavior of your schemas.
No library is going to write correct schemas for you.

Aside from that, this library follows the following principles:

1. Familiar behavior: This library strives to match the validation behavior of
   the (Draft 4) validator from `jsonschema`_.
2. Pro-active testing: This library includes and actively runs a comprehensive
   suite of tests to ensure behavior in the first point.
3. Documentation: This library includes a list outlining support for JSON
   Schema features/keywords, and strive to keep this up to date.


.. _tox: https://tox.readthedocs.io/en/latest/
.. _reasons listed here: https://github.com/alecthomas/voluptuous#why-use-voluptuous-over-another-validation-library
.. _jsonschema: https://github.com/Julian/jsonschema
