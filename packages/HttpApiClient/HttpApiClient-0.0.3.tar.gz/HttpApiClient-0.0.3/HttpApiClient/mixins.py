from __future__ import print_function, division, absolute_import, unicode_literals

from jsonschema import ValidationError
from jsonschema import Draft4Validator

from . import exceptions


class JsonResponseMixin(object):
    def clean_response(self, response, request):
        super(JsonResponseMixin, self).clean_response(response, request)
        try:
            result = response.json()
        except ValueError as e:
            raise self.ServerError(e, level='json')

        try:
            schema = request.schema
        except AttributeError:
            raise exceptions.JsonSchemaMissingError()

        try:
            Draft4Validator(schema).validate(result)
        except ValidationError as e:
            raise self.ServerError(e, schema=schema, level='json')

        return result
