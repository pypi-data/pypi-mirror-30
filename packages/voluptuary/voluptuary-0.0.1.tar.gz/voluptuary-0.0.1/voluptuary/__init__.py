import json
import warnings

from jsonschema import RefResolver

import voluptuous
from voluptuous import Schema, Any, All


class Validators(object):

    @staticmethod
    def ordered_array_validator(schemas, additional_items):
        """Validates an ordered array using an ordered list of schemas

        If additional_items is False, extra items are allowed past at the
        end of the array (you can have more items than schemas)
        """

        def _ordered_array_validator(value):
            if not isinstance(value, list):
                raise voluptuous.Invalid("not a list")
            if not additional_items and len(schemas) < len(value):
                raise voluptuous.Invalid(
                    "additional items {} are not allowed"
                    .format(value[len(schemas):])
                )
            print('_ordered_array_validator(%s)' % (value, ))
            for schema, v in zip(schemas, value):
                schema(v)
            return value

        return _ordered_array_validator


def _type_to_voluptuous(t):
    """Converts the `type` to a voluptuous schema"""


def to_voluptuous(schema):
    return Converter(schema).convert()


class Converter(object):

    def __init__(self, schema):
        self._entire_schema = schema
        self._resolver = RefResolver('', self._entire_schema)

    def convert(self):
        return self._convert(self._entire_schema)

    def _convert(self, schema):
        if not schema:
            return Schema(object)
        elif isinstance(schema, list):
            schemas = [self._convert(x) for x in schema]
            return Schema(Any(*schemas))
        elif isinstance(schema, dict) and '$ref' in schema:
            with self._resolver.resolving(schema['$ref']) as resolved:
                print('Followed ref: %s -> %s' % (schema['$ref'], resolved))
                return self._convert(resolved)
        elif isinstance(schema, dict) and 'type' in schema:
            result = self._convert(schema['type'])
            if 'properties' in schema:
                for key, val in schema.get('properties', {}).items():
                    result = result.extend({key: self._convert(val)})
            if 'additionalProperties' in schema:
                additional_properties = schema['additionalProperties']
                if additional_properties is False:
                    result.extra = voluptuous.PREVENT_EXTRA
                elif additional_properties is True:
                    result.extra = voluptuous.ALLOW_EXTRA
                else:
                    result = result.extend(
                        {
                            voluptuous.Extra: self.
                            _convert(additional_properties),
                        }
                    )
            if 'items' in schema:
                items = schema['items']
                length = voluptuous.Length(
                    min=schema.get('minItems'),
                    max=schema.get('maxItems'),
                )
                if isinstance(items, dict):
                    return Schema(All([self._convert(items)], length))
                elif isinstance(items, list):
                    array_validator = Validators.ordered_array_validator(
                        [self._convert(x) for x in items],
                        additional_items=schema.get('additionalItems', True),
                    )
                    return Schema(All(array_validator, length))
                else:
                    raise Exception(
                        "Invalid schema for `items`: {}".format(schema)
                    )
            return result
        elif isinstance(schema, dict) and 'anyOf' in schema:
            schemas = [self._convert(x) for x in schema['anyOf']]
            return Schema(Any(*schemas))
        elif isinstance(schema, dict) and 'allOf' in schema:
            schemas = [self._convert(x) for x in schema['allOf']]
            return Schema(All(*schemas))
        elif isinstance(schema, dict) and 'oneOf' in schema:
            schemas = [self._convert(x) for x in schema['oneOf']]
            return voluptuous.SomeOf(schemas, min_valid=1, max_valid=1)
        elif isinstance(
            schema, dict
        ) and ('minLength' in schema or 'maxLength' in schema):
            return voluptuous.Length(
                min=schema.get('minLength'),
                max=schema.get('maxLength'),
            )
        elif schema == 'string':
            return Schema(str)
        elif schema == 'integer':
            return Schema(int)
        elif schema == 'number':
            return Schema(Any(int, float))
        elif schema == 'boolean':
            return Schema(bool)
        elif schema == 'null':
            return Schema(None)
        elif schema == 'object':
            return Schema({}, extra=voluptuous.ALLOW_EXTRA)
        elif schema == 'array':
            return Schema(list)
        else:
            raise Exception("Failed to convert schema: %s" % schema)


def to_string(schema, warned=[]):
    if not warned:
        warnings.warn(
            '`to_string` is not intended for code generation and does not '
            'make any guarantee about the correctness of the string '
            'representation of your Voluptuous schema as Python code.'
        )
        warned.append(True)

    result = ''
    # Handling Schema
    if hasattr(schema, 'schema'):
        result += '%s(' % schema.__class__.__name__
        result += to_string(schema.schema)
        result += ')'
    # Handling _WithSubValidators
    elif hasattr(schema, 'validators'):
        result += '%s(' % schema.__class__.__name__
        result += ', '.join([to_string(v) for v in schema.validators])
        result += ')'
    elif isinstance(schema, list):
        result += '[' + ', '.join((to_string(x) for x in schema)) + ']'
    elif isinstance(schema, dict):
        result += '{'
        result += ', '.join(
            [
                '%s: %s' % (to_string(k), to_string(v))
                for k, v in sorted(schema.items(), key=lambda x: x[0])
            ]
        )
        result += '}'
    elif hasattr(schema, '__name__'):
        result += schema.__name__
    else:
        result += repr(schema)
    return result


if __name__ == '__main__':
    import sys
    with open(sys.argv[1]) as f:
        data = json.load(f)
    schema = to_voluptuous(data)
    print(repr(schema))
    print(to_string(schema))
