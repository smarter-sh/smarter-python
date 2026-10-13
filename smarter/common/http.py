"""
The SDK's http transport: authentication, retries, error mapping, and response parsing.

:class:`SmarterHttpClient` sends every request of a :class:`smarter.Smarter` client. It adds the
api key and the SDK's headers, retries requests that failed for transient reasons, raises a
:mod:`smarter.common.exceptions` error for a 4xx or 5xx response, and validates the response's
JSON against a Pydantic model.
"""

import logging
import random
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Optional, TypeVar, Union

import httpx
from pydantic import TypeAdapter, ValidationError

from smarter.__version__ import __version__
from smarter.models.chat import CHAT_CONTRACT_V2_CAPABILITY
from smarter.models.journal import SAMJournalApiErrorBody

from .conf import ClientConfig
from .exceptions import (
    APIConnectionError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
)
from .log import mask_secret
from .streaming import EVENT_STREAM_CONTENT_TYPE, ServerSentEvent, iter_sse

logger = logging.getLogger("smarter.client")

T = TypeVar("T")

QueryParamValue = Union[str, int, float, bool, None]
"""A query parameter's value.

None leaves the parameter out.
"""

USER_AGENT = f"smarter-python/{__version__}"
CLIENT_NAME = "smarter-python"
"""The SDK's ``X-Smarter-Client`` header, which identifies it to the platform's logs and journal."""

RETRYABLE_STATUSES = frozenset({408, 429, 502, 504})
"""Statuses that mean the request may succeed if it is sent again.

503 is retried only when the platform did not send it: see :func:`is_retryable`.
"""

MAX_RETRY_AFTER = 60.0
"""Seconds.

A longer ``Retry-After`` is not waited for.
"""

STATUS_ERRORS: dict[int, type[APIStatusError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: RateLimitError,
}


@lru_cache(maxsize=256)
def _type_adapter(cast_to: Any) -> TypeAdapter[Any]:
    """A cached TypeAdapter: building one is slower than validating with it."""
    return TypeAdapter(cast_to)


def parse_body(response: httpx.Response) -> object:
    """
    A response's body: its JSON, or its text when it is not JSON.

    :param response: The response, which must have been read.
    :returns: The parsed JSON, the text, or None for an empty body.
    """
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        return response.text


def journal_error(body: object) -> Optional[SAMJournalApiErrorBody]:
    """
    The Smarter Journal error of a response body, if it is a journaled error response.

    :param body: A parsed response body.
    :returns: The error body, or None.
    """
    if not isinstance(body, dict) or not isinstance(body.get("error"), dict):
        return None
    try:
        return SAMJournalApiErrorBody.model_validate(body["error"])
    except ValidationError:
        return None


def error_message(response: httpx.Response, body: object, error: Optional[SAMJournalApiErrorBody]) -> str:
    """
    A human-readable message for an error response.

    The platform's views return errors in several shapes: the journal's ``error`` object, an
    ``error`` string, Django REST framework's ``detail``, plain text, or a Django error page.

    :param response: The response.
    :param body: Its parsed body.
    :param error: Its journal error, if any.
    :returns: The message.
    """
    if error is not None:
        return error.description or error.errorClass
    if isinstance(body, dict):
        for key in ("error", "detail", "message"):
            value = body.get(key)
            if isinstance(value, str) and value:
                return value
        if isinstance(body.get("error"), dict) and isinstance(body["error"].get("description"), str):
            return body["error"]["description"]
    if isinstance(body, str) and body and "<html" not in body[:500].lower():
        return body[:500]
    return f"{response.status_code} {response.reason_phrase}".strip()


def make_status_error(response: httpx.Response) -> APIStatusError:
    """
    The exception for a 4xx or 5xx response, by its status.

    :param response: The response, which must have been read.
    :returns: e.g. a :class:`~smarter.common.exceptions.NotFoundError` for a 404.
    """
    body = parse_body(response)
    error = journal_error(body)
    message = error_message(response, body, error)
    status = response.status_code
    error_class = STATUS_ERRORS.get(status) or (InternalServerError if status >= 500 else APIStatusError)
    return error_class(message, response=response, body=body, error=error)


def is_retryable(response: httpx.Response) -> bool:
    """
    True if a failed response may succeed when the request is sent again.

    A 503 is retried only when it is not a journaled response. The Smarter platform itself answers
    503 for a resource that is not ready (e.g. ``SAMBrokerErrorNotReady``), which a retry won't
    change, whereas a 503 from a load balancer or proxy means the platform is briefly unavailable.

    :param response: The response, which must have been read.
    :returns: True to retry.
    """
    if response.status_code in RETRYABLE_STATUSES:
        return True
    if response.status_code == 503:
        return journal_error(parse_body(response)) is None
    return False


def retry_delay(attempt: int, response: Optional[httpx.Response] = None) -> float:
    """
    Seconds to wait before a retry: the response's ``Retry-After``, or exponential backoff with jitter.

    :param attempt: The number of the attempt that failed, from 0.
    :param response: The failed response, if there was one.
    :returns: The delay.
    """
    if response is not None:
        retry_after = response.headers.get("retry-after")
        try:
            seconds = float(retry_after) if retry_after is not None else None
        except ValueError:
            seconds = None
        if seconds is not None and 0 <= seconds <= MAX_RETRY_AFTER:
            return seconds
    return min(0.5 * 2**attempt, 8.0) * (1 - 0.25 * random.random())  # nosec B311 - jitter, not security


def query_params(params: Optional[Mapping[str, QueryParamValue]]) -> dict[str, str]:
    """
    Query parameters as strings: booleans as ``true`` or ``false``, and None values left out.

    :param params: The parameters.
    :returns: The parameters that httpx sends.
    """
    if not params:
        return {}
    result: dict[str, str] = {}
    for key, value in params.items():
        if value is None:
            continue
        result[key] = ("true" if value else "false") if isinstance(value, bool) else str(value)
    return result


class SmarterHttpClient:
    """
    Sends the requests of a Smarter client.

    :param config: The client's resolved configuration.
    :param default_headers: Headers to add to every request.
    :param http_client: An ``httpx.Client`` to use, e.g. with a proxy or a test transport. Its own
        base url and timeout are ignored.
    """

    def __init__(
        self,
        config: ClientConfig,
        *,
        default_headers: Optional[Mapping[str, str]] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self.config = config
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.Client(timeout=config.timeout, follow_redirects=False)
        self._default_headers = dict(default_headers or {})

    @property
    def base_url(self) -> str:
        """The api's base url, e.g. ``https://platform.smarter.sh/api/v1/``."""
        return self.config.base_url

    @property
    def max_retries(self) -> int:
        """How many times a failed request is retried."""
        return self.config.max_retries

    def url(self, path: str) -> str:
        """
        The absolute url of an api path.

        :param path: A path relative to the base url, e.g. ``cli/whoami/``. An absolute url is returned as is.
        :returns: The url.
        """
        if path.startswith(("http://", "https://")):
            return path
        return self.base_url + path.lstrip("/")

    def headers(self, extra: Optional[Mapping[str, str]] = None) -> dict[str, str]:
        """
        The headers of a request.

        :param extra: Headers for this request, which override the defaults.
        :returns: The headers.
        """
        headers = {
            "Authorization": f"Token {self.config.api_key.get_secret_value()}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
            "X-Smarter-Client": CLIENT_NAME,
            "X-Smarter-Capabilities": CHAT_CONTRACT_V2_CAPABILITY,
        }
        headers.update(self._default_headers)
        headers.update(extra or {})
        return headers

    def build_request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, QueryParamValue]] = None,
        json: object = None,
        content: Union[str, bytes, None] = None,
        files: Optional[Mapping[str, Any]] = None,
        data: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> httpx.Request:
        """
        Build a request.

        See :meth:`request` for the parameters.

        :returns: The request.
        """
        return self._http_client.build_request(
            method,
            self.url(path),
            params=query_params(params),
            json=json,
            content=content,
            files=files,
            data=data,
            headers=self.headers(headers),
            timeout=timeout if timeout is not None else self.config.timeout,
        )

    def send(self, request: httpx.Request, *, stream: bool = False) -> httpx.Response:
        """
        Send a request, with retries, and raise for an error status.

        :param request: The request.
        :param stream: True to return before the body is read, for Server-Sent Events. The caller
            must close the response.
        :returns: The successful response.
        :raises APIConnectionError: If no response was received after the retries.
        :raises APITimeoutError: If the request timed out after the retries.
        :raises APIStatusError: For a 4xx or 5xx response, as the status's subclass.
        """
        attempt = 0
        while True:
            started = time.monotonic()
            try:
                response = self._http_client.send(request, stream=stream)
            except httpx.TimeoutException as e:
                if attempt < self.max_retries:
                    self._wait(attempt, request, reason="timeout")
                    attempt += 1
                    continue
                raise APITimeoutError(request) from e
            except httpx.TransportError as e:
                if attempt < self.max_retries:
                    self._wait(attempt, request, reason=type(e).__name__)
                    attempt += 1
                    continue
                raise APIConnectionError(request, message=f"Connection error: {e}") from e

            logger.info(
                "%s %s -> %s in %.2fs",
                request.method,
                request.url,
                response.status_code,
                time.monotonic() - started,
            )
            if response.is_success:
                return response
            response.read()
            response.close()
            if attempt < self.max_retries and is_retryable(response):
                self._wait(attempt, request, reason=str(response.status_code), response=response)
                attempt += 1
                continue
            raise make_status_error(response)

    def _wait(
        self, attempt: int, request: httpx.Request, *, reason: str, response: Optional[httpx.Response] = None
    ) -> None:
        delay = retry_delay(attempt, response)
        logger.info("retrying %s %s in %.2fs after %s", request.method, request.url, delay, reason)
        time.sleep(delay)

    def request(
        self,
        method: str,
        path: str,
        *,
        cast_to: Any,
        params: Optional[Mapping[str, QueryParamValue]] = None,
        json: object = None,
        content: Union[str, bytes, None] = None,
        files: Optional[Mapping[str, Any]] = None,
        data: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Send a request, and validate its JSON response.

        :param method: The http method, e.g. ``GET``.
        :param path: The path, relative to the api's base url, e.g. ``guardrails/``.
        :param cast_to: The type of the response's JSON, e.g. ``Guardrail`` or ``list[Guardrail]``.
            ``None`` ignores the body.
        :param params: Query parameters.
        :param json: A JSON body.
        :param content: A raw body, e.g. a YAML manifest.
        :param files: Files, for a multipart/form-data body.
        :param data: Form fields, for a multipart/form-data body.
        :param headers: Headers for this request.
        :param timeout: The timeout in seconds, instead of the client's.
        :returns: The validated response, an instance of ``cast_to``.
        :raises APIResponseValidationError: If the response does not match ``cast_to``.
        """
        request = self.build_request(
            method,
            path,
            params=params,
            json=json,
            content=content,
            files=files,
            data=data,
            headers=headers,
            timeout=timeout,
        )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "request %s %s api_key=%s body=%s",
                method,
                request.url,
                mask_secret(self.config.api_key.get_secret_value()),
                request.content[:2000] if not files else "<multipart>",
            )
        response = self.send(request)
        body = parse_body(response)
        logger.debug("response %s %s", response.status_code, str(body)[:2000])
        if cast_to is None:
            return None
        try:
            return _type_adapter(cast_to).validate_python(body)
        except ValidationError as e:
            raise APIResponseValidationError(
                response, body, f"The response of {method} {request.url} does not match {cast_to}: {e}"
            ) from e

    @contextmanager
    def stream_events(
        self,
        method: str,
        path: str,
        *,
        json: object = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Iterator[Iterator[ServerSentEvent]]:
        """
        Send a request that asks for Server-Sent Events, and iterate its events.

        .. code-block:: python

            with http.stream_events("POST", "llm-clients/5/prompt/", json=body) as events:
                for event in events:
                    ...

        :param method: The http method.
        :param path: The path, relative to the api's base url.
        :param json: A JSON body.
        :param headers: Headers for this request.
        :param timeout: The timeout in seconds, instead of the client's. It applies to each read.
        :returns: A context manager whose value iterates the events. The response is closed on exit.
        """
        request = self.build_request(
            method,
            path,
            json=json,
            headers={"Accept": EVENT_STREAM_CONTENT_TYPE, **dict(headers or {})},
            timeout=timeout,
        )
        response = self.send(request, stream=True)
        try:
            yield iter_sse(response.iter_lines())
        finally:
            response.close()

    def close(self) -> None:
        """Close the underlying ``httpx.Client``, unless it was passed in by the caller."""
        if self._owns_http_client:
            self._http_client.close()


__all__ = [
    "CLIENT_NAME",
    "QueryParamValue",
    "SmarterHttpClient",
    "USER_AGENT",
    "error_message",
    "is_retryable",
    "journal_error",
    "make_status_error",
    "parse_body",
    "query_params",
    "retry_delay",
]
