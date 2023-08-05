from __future__ import print_function, division, absolute_import, unicode_literals

import json
import copy
import logging

from requests.auth import HTTPBasicAuth

from .base import BaseApiClient, DEFAULT_TIMEOUT
from .request import ApiRequest
from .mixins import JsonResponseMixin


log = logging.getLogger(__name__)


class ApiClient(JsonResponseMixin, BaseApiClient):

    def __init__(self, host, api_version, app_id, username, password):
        self.base_url = '{}{}/app/{}/'.format(host, api_version, app_id)
        self.auth = HTTPBasicAuth(username, password)
        super(ApiClient, self).__init__()

    def call(self, method, method_name, _schema=None, _timeout=DEFAULT_TIMEOUT, _idempotent=False,
             _headers=None, as_json=False, **params):
        headers = copy.deepcopy(_headers) or dict()

        if as_json:
            headers['content-type'] = 'application/json'
            params = json.dumps(params)

        request = ApiRequest(
            method=method,
            url=method_name,
            data=params,
            auth=self.auth,
            headers=headers,
            is_idempotent=_idempotent)

        request.schema = _schema
        return self.request(request, timeout=_timeout)

    def clean_response(self, response, request):
        try:
            result = super(ApiClient, self).clean_response(response, request)
        except self.ClientError as error:
            # if request query is invalid
            # added error message
            if error.code == 400:
                json_response = response.json()
                error = self.ClientError(
                    level=error.level,
                    code=error.code,
                    status_text=error.status_text,
                    description=json_response.get('message') or json_response,
                )

            raise error

        return result
