"""
The exceptions of the Smarter Python SDK.

Every exception that the SDK raises is a :class:`SmarterError`, so a caller can catch them all with
one ``except`` clause. This follows the Smarter platform's own rule (ADR-012) that exceptions
subclass one hierarchy.

The api errors mirror the http status that the Smarter api returned:

.. code-block:: text

    SmarterError
    ├── SmarterConfigurationError        the client has no api key or base url
    ├── SmarterValueError                an argument is invalid, before any request is sent
    ├── ResourceNotFoundError            a resource was not found, by the api (NotFoundError) or by find()
    └── APIError
        ├── APIConnectionError           the request never got a response
        │   └── APITimeoutError
        ├── APIResponseValidationError   the response does not match the SDK's model of it
        └── APIStatusError               the api returned a 4xx or 5xx status
            ├── BadRequestError          400
            ├── AuthenticationError      401
            ├── PermissionDeniedError    403
            ├── NotFoundError            404, also a ResourceNotFoundError
            ├── ConflictError            409
            ├── UnprocessableEntityError 422
            ├── RateLimitError           429
            └── InternalServerError      5xx
"""

from typing import TYPE_CHECKING, Optional

import httpx

if TYPE_CHECKING:
    from smarter.models.journal import SAMJournalApiErrorBody


class SmarterError(Exception):
    """The base class of every exception that the Smarter SDK raises."""


class SmarterConfigurationError(SmarterError):
    """The client is missing configuration that it needs, e.g. an api key or a base url."""


class SmarterValueError(SmarterError, ValueError):
    """An argument is invalid.

    Raised before a request is sent.
    """


class ResourceNotFoundError(SmarterError, LookupError):
    """A resource was not found: the api answered 404 (:class:`NotFoundError`), or ``find()`` found no resource of that name."""


class APIError(SmarterError):
    """
    A request to the Smarter api failed.

    :param message: A human-readable description of the error.
    :param request: The http request that failed.
    :param body: The response's parsed JSON body, or its text, or None when there is no response.
    """

    def __init__(self, message: str, request: httpx.Request, *, body: object = None) -> None:
        super().__init__(message)
        self.message = message
        self.request = request
        self.body = body


class APIConnectionError(APIError):
    """The request did not get a response, e.g. the server is unreachable."""

    def __init__(self, request: httpx.Request, message: str = "Connection error.") -> None:
        super().__init__(message, request)


class APITimeoutError(APIConnectionError):
    """The request timed out."""

    def __init__(self, request: httpx.Request) -> None:
        super().__init__(request, message="Request timed out.")


class APIResponseValidationError(APIError):
    """
    The api's response does not match the SDK's model of it.

    This usually means that the SDK and the Smarter platform are of incompatible versions.

    :param response: The http response.
    :param body: The response's parsed JSON body.
    :param message: A description of the mismatch.
    """

    def __init__(self, response: httpx.Response, body: object, message: str) -> None:
        super().__init__(message, response.request, body=body)
        self.response = response
        self.status_code = response.status_code


class APIStatusError(APIError):
    """
    The api returned a 4xx or 5xx status.

    :param message: The error's description, from the response when it has one.
    :param response: The http response.
    :param body: The response's parsed JSON body, or its text.
    :param error: The Smarter Journal error body, when the response is a journaled error.
    """

    def __init__(
        self,
        message: str,
        *,
        response: httpx.Response,
        body: object,
        error: Optional["SAMJournalApiErrorBody"] = None,
    ) -> None:
        super().__init__(message, response.request, body=body)
        self.response = response
        self.status_code = response.status_code
        self.error = error

    @property
    def error_class(self) -> Optional[str]:
        """The name of the server-side exception class, e.g. ``SAMBrokerErrorNotFound``, when the platform sent it."""
        return self.error.errorClass if self.error else None

    def __str__(self) -> str:
        return f"Error code: {self.status_code} - {self.message}"


class BadRequestError(APIStatusError):
    """400: the request is invalid, e.g. a malformed manifest."""


class AuthenticationError(APIStatusError):
    """401: the api key is missing, invalid, or inactive."""


class PermissionDeniedError(APIStatusError):
    """403: the api key's user may not perform the operation."""


class NotFoundError(APIStatusError, ResourceNotFoundError):
    """404: the resource does not exist, or the api key's user may not read it."""


class ConflictError(APIStatusError):
    """409: the request conflicts with the resource's current state."""


class UnprocessableEntityError(APIStatusError):
    """422: the request is well-formed but cannot be processed."""


class RateLimitError(APIStatusError):
    """429: too many requests."""


class InternalServerError(APIStatusError):
    """5xx: the platform failed to process the request."""


__all__ = [
    "APIConnectionError",
    "APIError",
    "APIResponseValidationError",
    "APIStatusError",
    "APITimeoutError",
    "AuthenticationError",
    "BadRequestError",
    "ConflictError",
    "InternalServerError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "ResourceNotFoundError",
    "SmarterConfigurationError",
    "SmarterError",
    "SmarterValueError",
    "UnprocessableEntityError",
]
