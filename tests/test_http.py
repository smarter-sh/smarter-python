"""Test smarter.core.http."""

import logging
from unittest import mock

import httpx

from smarter.core import http
from smarter.core.exceptions import (
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
from smarter.models.platform import WhoAmI

from .base import API, API_KEY, SmarterTestBase


def response(status: int, **kwargs) -> httpx.Response:
    """A response to a GET request, with its body read."""
    return httpx.Response(status, request=httpx.Request("GET", API), **kwargs)


class TestHttpHelpers(SmarterTestBase):
    """Test the transport's helper functions."""

    def test_query_params(self):
        """Booleans become true and false, and None values are left out."""
        self.assertEqual(
            http.query_params({"a": True, "b": False, "c": None, "d": 3}), {"a": "true", "b": "false", "d": "3"}
        )
        self.assertEqual(http.query_params(None), {})

    def test_parse_body(self):
        """A body is its JSON, its text, or None when it is empty."""
        self.assertEqual(http.parse_body(response(200, json={"a": 1})), {"a": 1})
        self.assertEqual(http.parse_body(response(200, text="plain")), "plain")
        self.assertIsNone(http.parse_body(response(204)))

    def test_error_messages(self):
        """Each of the platform's error shapes gives a readable message."""
        journaled = self.load_json("describe_missing")
        cases = [
            (journaled, journaled["error"]["description"]),
            ({"error": "text is required."}, "text is required."),
            ({"detail": "Not found."}, "Not found."),
            ({"error": {"description": "nested"}}, "nested"),
            ("Forbidden: no", "Forbidden: no"),
            ("<html><body>debug page</body></html>", "500 Internal Server Error"),
            (None, "500 Internal Server Error"),
        ]
        for body, expected in cases:
            with self.subTest(body=str(body)[:40]):
                kwargs = {"json": body} if isinstance(body, dict) else {"text": body or ""}
                r = response(500, **kwargs)
                self.assertEqual(
                    http.error_message(r, http.parse_body(r), http.journal_error(http.parse_body(r))), expected
                )

    def test_status_errors(self):
        """Each status raises its own exception class."""
        cases = {
            400: BadRequestError,
            401: AuthenticationError,
            403: PermissionDeniedError,
            404: NotFoundError,
            409: ConflictError,
            422: UnprocessableEntityError,
            429: RateLimitError,
            500: InternalServerError,
            503: InternalServerError,
            418: APIStatusError,
        }
        for status, error_class in cases.items():
            with self.subTest(status=status):
                self.assertIs(type(http.make_status_error(response(status, json={}))), error_class)

    def test_journal_error(self):
        """A journaled error response's error is parsed, and anything else is not."""
        error = http.make_status_error(response(404, json=self.load_json("describe_missing"))).error
        self.assertEqual(error.errorClass, "SAMBrokerErrorNotReady")  # type: ignore[union-attr]
        self.assertIsNone(http.journal_error({"error": {"unexpected": True}}))
        self.assertIsNone(http.journal_error(["not", "a", "dict"]))

    def test_is_retryable(self):
        """Transient statuses are retried, and a 503 only when the platform did not send it."""
        self.assertTrue(http.is_retryable(response(502)))
        self.assertTrue(http.is_retryable(response(429)))
        self.assertTrue(http.is_retryable(response(503, text="Service Unavailable")))
        self.assertFalse(http.is_retryable(response(503, json=self.load_json("describe_missing"))))
        self.assertFalse(http.is_retryable(response(500)))
        self.assertFalse(http.is_retryable(response(404)))

    def test_retry_delay(self):
        """Retry-After is honored up to a limit, and otherwise the delay backs off exponentially."""
        self.assertEqual(http.retry_delay(0, response(429, headers={"retry-after": "3"})), 3.0)
        self.assertLessEqual(http.retry_delay(0, response(429, headers={"retry-after": "3600"})), 0.5)
        self.assertLessEqual(http.retry_delay(0, response(429, headers={"retry-after": "soon"})), 0.5)
        self.assertGreater(http.retry_delay(3), 2.9)
        self.assertLessEqual(http.retry_delay(10), 8.0)


class TestSmarterHttpClient(SmarterTestBase):
    """Test the transport."""

    def test_headers(self):
        """Every request carries the api key, the SDK's identity, and the chat contract version."""
        self.route("POST", "cli/whoami/", fixture="whoami")
        client = self.make_client(default_headers={"X-Custom": "1"})
        client.whoami()
        headers = self.last_request.headers
        self.assertEqual(headers["authorization"], f"Token {API_KEY}")
        self.assertEqual(headers["x-smarter-client"], http.CLIENT_NAME)
        self.assertEqual(headers["x-smarter-capabilities"], "chat-contract-v2")
        self.assertTrue(headers["user-agent"].startswith("smarter-python/"))
        self.assertEqual(headers["x-custom"], "1")

    def test_url(self):
        """Paths are relative to the api's base url, and absolute urls are kept."""
        self.assertEqual(self.client.http.url("/cli/whoami/"), f"{API}cli/whoami/")
        self.assertEqual(self.client.http.url("https://other/x"), "https://other/x")

    def test_retries_then_succeeds(self):
        """A transient failure is retried, and the retry's response is returned."""
        statuses = iter([502, 200])

        def handler(_request):
            status = next(statuses)
            return httpx.Response(status, json=self.load_json("whoami") if status == 200 else {})

        self.route("POST", "cli/whoami/", handler=handler)
        client = self.make_client(max_retries=2)
        with mock.patch.object(http.time, "sleep") as sleep:
            self.assertIsInstance(client.whoami(), WhoAmI)
        sleep.assert_called_once()

    def test_retries_exhausted(self):
        """A failure that persists through the retries is raised."""
        self.route("POST", "cli/whoami/", status=429, json_body={"detail": "slow down"})
        client = self.make_client(max_retries=2)
        with mock.patch.object(http.time, "sleep") as sleep, self.assertRaises(RateLimitError):
            client.whoami()
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(len(self.requests), 3)

    def test_no_retry_for_client_errors(self):
        """A 4xx other than 408 and 429 is raised at once."""
        self.route("POST", "cli/whoami/", status=401, json_body={"detail": "Invalid token."})
        client = self.make_client(max_retries=3)
        with self.assertRaises(AuthenticationError) as context:
            client.whoami()
        self.assertEqual(context.exception.message, "Invalid token.")
        self.assertEqual(len(self.requests), 1)

    def test_timeout(self):
        """A timeout is retried, then raised as an APITimeoutError."""

        def handler(request):
            raise httpx.ReadTimeout("slow", request=request)

        self.route("POST", "cli/whoami/", handler=handler)
        client = self.make_client(max_retries=1)
        with mock.patch.object(http.time, "sleep"), self.assertRaises(APITimeoutError):
            client.whoami()
        self.assertEqual(len(self.requests), 2)

    def test_connection_error(self):
        """A connection failure is retried, then raised as an APIConnectionError."""

        def handler(request):
            raise httpx.ConnectError("refused", request=request)

        self.route("POST", "cli/whoami/", handler=handler)
        client = self.make_client(max_retries=1)
        with mock.patch.object(http.time, "sleep"), self.assertRaises(APIConnectionError) as context:
            client.whoami()
        self.assertIn("refused", context.exception.message)

    def test_response_validation_error(self):
        """A response that doesn't match its model raises APIResponseValidationError."""
        self.route("POST", "cli/whoami/", json_body={"data": {"user": "not an object"}})
        with self.assertRaises(APIResponseValidationError) as context:
            self.client.whoami()
        self.assertEqual(context.exception.status_code, 200)

    def test_cast_to_none(self):
        """A request whose body is not needed returns None."""
        self.route("DELETE", "x/", status=204)
        self.assertIsNone(self.client.http.request("DELETE", "x/", cast_to=None))

    def test_debug_logging(self):
        """Debug logging logs the request with a masked api key, never the key itself."""
        self.route("POST", "cli/whoami/", fixture="whoami")
        with self.assertLogs("smarter.client", level=logging.DEBUG) as logs:
            self.client.whoami()
        output = "\n".join(logs.output)
        self.assertIn("****beef", output)
        self.assertNotIn(API_KEY, output)

    def test_stream_events(self):
        """A stream's events are parsed, and the request asks for Server-Sent Events."""
        self.route("POST", "llm-clients/5/prompt/", text=self.load_text("prompt_sse.txt"))
        with self.client.http.stream_events("POST", "llm-clients/5/prompt/", json={}) as events:
            names = [event.event for event in events]
        self.assertEqual(names[-1], "result")
        self.assertEqual(self.last_request.headers["accept"], "text/event-stream")

    def test_close(self):
        """The client closes an httpx client that it created, and not one that it was given."""
        given = httpx.Client()
        self.addCleanup(given.close)
        transport = http.SmarterHttpClient(self.client.config, http_client=given)
        transport.close()
        self.assertFalse(given.is_closed)
        owned = http.SmarterHttpClient(self.client.config)
        owned.close()
        self.assertTrue(owned._http_client.is_closed)  # pylint: disable=protected-access
