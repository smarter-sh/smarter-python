"""Test smarter.core.exceptions."""

import unittest

import httpx

from smarter.core import exceptions
from smarter.models.journal import SAMJournalApiErrorBody


class TestExceptions(unittest.TestCase):
    """Test the exception hierarchy."""

    def setUp(self):
        self.request = httpx.Request("GET", "http://testserver/api/v1/guardrails/")
        self.response = httpx.Response(404, request=self.request)

    def test_every_exception_is_a_smarter_error(self):
        """One except clause catches every exception that the SDK raises."""
        for name in exceptions.__all__:
            with self.subTest(name=name):
                self.assertTrue(issubclass(getattr(exceptions, name), exceptions.SmarterError))

    def test_not_found_is_a_resource_not_found_error(self):
        """A 404 and a failed find() are caught by one except clause."""
        self.assertTrue(issubclass(exceptions.NotFoundError, exceptions.ResourceNotFoundError))
        self.assertTrue(issubclass(exceptions.ResourceNotFoundError, LookupError))

    def test_status_error(self):
        """A status error carries its response, status and journal error."""
        error = SAMJournalApiErrorBody(errorClass="SAMBrokerErrorNotFound", status=404, description="gone")
        e = exceptions.NotFoundError("gone", response=self.response, body={"error": {}}, error=error)
        self.assertEqual(e.status_code, 404)
        self.assertEqual(e.error_class, "SAMBrokerErrorNotFound")
        self.assertEqual(str(e), "Error code: 404 - gone")
        self.assertIs(e.request, self.request)
        self.assertIsNone(exceptions.APIStatusError("x", response=self.response, body=None).error_class)

    def test_connection_errors(self):
        """Connection and timeout errors carry their request."""
        self.assertEqual(exceptions.APIConnectionError(self.request).message, "Connection error.")
        self.assertEqual(exceptions.APITimeoutError(self.request).message, "Request timed out.")
        self.assertIsInstance(exceptions.APITimeoutError(self.request), exceptions.APIConnectionError)

    def test_validation_error(self):
        """A validation error carries its response and body."""
        e = exceptions.APIResponseValidationError(self.response, {"a": 1}, "mismatch")
        self.assertEqual(e.status_code, 404)
        self.assertEqual(e.body, {"a": 1})

    def test_value_error(self):
        """SmarterValueError is also a ValueError."""
        self.assertTrue(issubclass(exceptions.SmarterValueError, ValueError))
