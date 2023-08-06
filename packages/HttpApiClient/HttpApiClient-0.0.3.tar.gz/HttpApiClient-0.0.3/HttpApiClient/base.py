from __future__ import print_function, division, absolute_import, unicode_literals
import six
import time
import logging
import requests
from six.moves import urllib

from .exceptions import ApiClientError, ApiServerError

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = object()


class BaseApiClientMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        klass = super(BaseApiClientMetaclass, mcs).__new__(mcs, name, bases, attrs)

        class ClientError(ApiClientError):
            client_class = klass

        class ServerError(ApiServerError):
            client_class = klass

        klass.ClientError = ClientError
        klass.ServerError = ServerError
        return klass


class BaseApiClient(six.with_metaclass(BaseApiClientMetaclass)):
    base_url = None
    default_timeout = 6.1  # slightly larger than a multiple of 3, which is the default TCP packet retransmission window
    max_tries = 3
    retry_backoff_factor = 0.5

    def __init__(self):
        self.session = requests.session()

    def request(self, request, timeout=DEFAULT_TIMEOUT):
        request.url = urllib.parse.urljoin(self.base_url, request.url)
        prepared = self.session.prepare_request(request)

        if timeout is DEFAULT_TIMEOUT:
            timeout = self.default_timeout

        errors = []
        backoff_time = self.retry_backoff_factor
        for try_idx in range(self.max_tries):
            log.debug('Trying request %s %s (%d/%d tries)', request.method, request.url, try_idx + 1, self.max_tries)

            if try_idx > 0:
                time.sleep(backoff_time)
                backoff_time *= 2

            try:
                return self._request_once(request, prepared, timeout)
            except self.ClientError as e:
                if e.permanent:
                    raise e
            except self.ServerError as e:
                if not request.is_idempotent and e.has_side_effects:
                    raise e

            log.debug('Request failed: %r', e)
            errors.append(e)

        raise errors[-1]

    def _request_once(self, request, prepeared, timeout):
        try:
            response = self.session.send(prepeared, timeout=timeout)
        except requests.ConnectionError as e:
            raise self.ServerError(level='socket', reason=e, has_side_effects=False)
        except requests.Timeout as e:
            raise self.ServerError(level='socket', reason=e)
        except requests.TooManyRedirects as e:
            raise self.ServerError(level='security', reason=e)

        return self.clean_response(response, request)

    def clean_response(self, response, request):
        """
        TODO: add general doc here

        If raised ClientError has attribute permanent=False then request may be retried even for
        non-idempotent request. For example - rate limit error.

        If raised ServerError has attribute has_side_effects=False then request may be retried even for
        non-idempotent request. For example - http 503.
        """
        code = response.status_code

        if 400 <= code < 500:
            raise self.ClientError(level='http', code=code, status_text=response.reason)

        elif 500 <= code < 600:
            raise self.ServerError(level='http', code=code, status_text=response.reason)

        return response.content


class SocialException(Exception):
    """Base social exception."""


class SocialExternalError(SocialException):
    """Something wrong happened on the other side."""


class SocialClientError(SocialException):
    """Something is wrong in our request."""


class SocialClientUserError(SocialClientError):
    """Something is wrong in user request."""


class SocialUnauthorizedError(SocialClientUserError):
    """Authentication data in request is missing or invalid (aka 401)."""


class SocialForbiddenError(SocialClientUserError):
    """Authentication is successful.
    But the user or this authentication data doesn't have enough permissions (aka 403)."""


class BaseSocialApiClientMetaclass(BaseApiClientMetaclass):
    def __new__(mcs, name, bases, attrs):
        klass = super(BaseSocialApiClientMetaclass, mcs).__new__(mcs, name, bases, attrs)

        class ClientError(SocialClientError, klass.ClientError):
            pass

        class ClientUserError(SocialClientUserError, ClientError):
            pass

        class ExternalError(SocialExternalError, klass.ServerError):
            pass

        class UnauthorizedError(SocialUnauthorizedError, ClientError):
            pass

        class ForbiddenError(SocialForbiddenError, ClientError):
            pass

        klass.ClientError = ClientError
        klass.ClientUserError = ClientUserError
        klass.ServerError = ExternalError
        klass.ExternalError = ExternalError
        klass.UnauthorizedError = UnauthorizedError
        klass.ForbiddenError = ForbiddenError

        return klass


class BaseSocialApiClient(six.with_metaclass(BaseSocialApiClientMetaclass, BaseApiClient)):
    pass
