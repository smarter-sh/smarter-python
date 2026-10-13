"""Test smarter.resources.guardrails."""

from smarter.core.exceptions import BadRequestError

from .base import SmarterTestBase


class TestGuardrails(SmarterTestBase):
    """Test Guardrails."""

    def test_list(self):
        """Guardrails are listed with their own fields."""
        self.route("GET", "guardrails/", fixture="guardrails")
        guardrail = self.client.guardrails.list()[0]
        self.assertEqual(guardrail.stage, "output")
        self.assertEqual(guardrail.config, {"detectors": ["credit_card", "us_ssn", "email", "phone_number", "iban"]})

    def test_evaluate(self):
        """Evaluate() sends the text and stage, and returns the findings."""
        self.route("POST", "guardrails/17/evaluate/", fixture="guardrail_eval")
        result = self.client.guardrails.evaluate(17, "my email is jane@example.com", stage="output")
        self.assertTrue(result.triggered)
        self.assertEqual(result.findings[0].matches[0].label, "email")
        self.assertEqual(self.request_json(), {"text": "my email is jane@example.com", "stage": "output"})

    def test_evaluate_rejected(self):
        """The platform's validation error is raised with its message."""
        self.route("POST", "guardrails/17/evaluate/", status=400, json_body={"error": "text is required."})
        with self.assertRaises(BadRequestError) as context:
            self.client.guardrails.evaluate(17, "")
        self.assertEqual(context.exception.message, "text is required.")

    def test_events(self):
        """Events() passes its filters as query parameters."""
        self.route("GET", "guardrails/17/events/", fixture="guardrail_events")
        events = self.client.guardrails.events(17, reviewed=False, disposition="blocked")
        self.assertEqual(events.guardrail, "pii_leak_output")
        self.assertEqual(dict(self.last_request.url.params), {"reviewed": "false", "disposition": "blocked"})
        self.client.guardrails.events(17)
        self.assertEqual(dict(self.last_request.url.params), {})

    def test_manifest_operations(self):
        """Describe, delete, example_manifest and json_schema use the Guardrail kind."""
        self.route("POST", "cli/describe/Guardrail/", json_body={"data": self.load_json("example_guardrail")["data"]})
        self.route("POST", "cli/delete/Guardrail/", json_body={"message": "deleted"})
        self.route("POST", "cli/example-manifest/Guardrail/", fixture="example_guardrail")
        self.route("POST", "cli/json-schema/Guardrail/", fixture="schema_secret")
        self.route("POST", "cli/apply/", json_body={"message": "applied"})
        self.assertEqual(self.client.guardrails.describe("x").kind, "Guardrail")
        self.assertEqual(self.client.guardrails.delete("x").message, "deleted")
        manifest = self.client.guardrails.example_manifest()
        self.assertEqual(self.client.guardrails.apply(manifest).message, "applied")
        self.assertTrue(self.client.guardrails.json_schema())
