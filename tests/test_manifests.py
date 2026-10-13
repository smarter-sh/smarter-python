"""Test smarter.resources.manifests and smarter.resources.base."""

import json
import tempfile
from pathlib import Path

from smarter.core.exceptions import (
    BadRequestError,
    InternalServerError,
    SmarterValueError,
)
from smarter.models.manifest import Manifest
from smarter.models.sam import SAMGuardrail
from smarter.resources.base import resource_id, to_manifest
from smarter.resources.manifests import kind_segment

from .base import SmarterTestBase


class TestManifests(SmarterTestBase):
    """Test the manifest api."""

    def setUp(self):
        super().setUp()
        self.example = self.load_json("example_guardrail")["data"]

    def test_apply(self):
        """Apply() sends the manifest as JSON, without its status, and returns the platform's message."""
        self.route("POST", "cli/apply/", json_body={"message": "applied", "api": "smarter.sh/v1"})
        response = self.client.manifests.apply({**self.example, "status": {"x": 1}})
        self.assertEqual(response.message, "applied")
        self.assertEqual(self.request_json()["metadata"]["name"], self.example["metadata"]["name"])
        self.assertNotIn("status", self.request_json())

    def test_apply_rejected(self):
        """A rejected manifest raises the platform's error."""
        self.route("POST", "cli/apply/", status=400, fixture="get_bad")
        with self.assertRaises(BadRequestError) as context:
            self.client.manifests.apply(self.example)
        self.assertEqual(context.exception.error_class, "APIV1CLIViewBadRequestError")

    def test_validate(self):
        """Validate() returns whether the manifest is valid."""
        self.route("POST", "cli/validate/", fixture="validate")
        self.assertTrue(self.client.manifests.validate(self.example).valid)
        self.route("POST", "cli/validate/", json_body={"message": "no data"})
        self.assertFalse(self.client.manifests.validate(self.example).valid)

    def test_get(self):
        """Get() returns the table, and filters it by name."""
        self.route("POST", "cli/get/LLMClient/", fixture="get_llmclient")
        result = self.client.manifests.get("LLMClient")
        self.assertEqual(len(result.items), 2)
        name = result.names[0]
        filtered = self.client.manifests.get("LLMClient", name)
        self.assertEqual(filtered.names, [name])
        self.assertEqual(filtered.metadata.count, 1)
        self.assertEqual(self.last_request.url.params["name"], name)
        self.route("POST", "cli/get/LLMClient/", json_body={"api": "smarter.sh/v1"})
        self.assertEqual(self.client.manifests.get("LLMClient").items, [])

    def test_describe(self):
        """Describe() returns the manifest, with its status."""
        self.route("POST", "cli/describe/LLMClient/", fixture="describe_llmclient")
        manifest = self.client.manifests.describe("LLMClient", "calculator")
        self.assertEqual(manifest.metadata.name, "calculator")
        self.assertIsNotNone(manifest.status)
        self.assertEqual(self.last_request.url.params["name"], "calculator")

    def test_describe_missing(self):
        """A missing resource raises the platform's error, and an empty response a SmarterValueError."""
        self.route("POST", "cli/describe/LLMClient/", status=503, fixture="describe_missing")
        with self.assertRaises(InternalServerError):
            self.client.manifests.describe("LLMClient", "nope")
        self.route("POST", "cli/describe/LLMClient/", json_body={"api": "smarter.sh/v1"})
        with self.assertRaises(SmarterValueError):
            self.client.manifests.describe("LLMClient", "nope")

    def test_verbs(self):
        """Delete, deploy, undeploy and logs post to their endpoints, with the name."""
        for verb in ("delete", "deploy", "undeploy", "logs"):
            self.route("POST", f"cli/{verb}/LLMClient/", json_body={"message": verb})
            with self.subTest(verb=verb):
                self.assertEqual(getattr(self.client.manifests, verb)("LLMClient", "calculator").message, verb)
                self.assertEqual(self.last_request.url.params["name"], "calculator")

    def test_example_manifest_and_json_schema(self):
        """Example_manifest() and json_schema() return the kind's example and schema."""
        self.route("POST", "cli/example-manifest/Guardrail/", fixture="example_guardrail")
        self.route("POST", "cli/json-schema/Secret/", fixture="schema_secret")
        self.assertEqual(self.client.manifests.example_manifest("Guardrail").kind, "Guardrail")
        self.assertIn("properties", self.client.manifests.json_schema("Secret"))
        self.route("POST", "cli/example-manifest/Guardrail/", json_body={"api": "smarter.sh/v1"})
        with self.assertRaises(SmarterValueError):
            self.client.manifests.example_manifest("Guardrail")
        self.route("POST", "cli/json-schema/Secret/", json_body={"api": "smarter.sh/v1"})
        self.assertEqual(self.client.manifests.json_schema("Secret"), {})

    def test_kind_segment(self):
        """A kind must be a single identifier."""
        self.assertEqual(kind_segment(" LLMClient "), "LLMClient")
        for kind in ("", "a/b", "a b"):
            with self.subTest(kind=kind), self.assertRaises(SmarterValueError):
                kind_segment(kind)


class TestResourceBase(SmarterTestBase):
    """Test the helpers of smarter.resources.base."""

    def test_to_manifest(self):
        """A manifest is accepted as a Manifest, a SAM model, a dict, YAML text, or a file path."""
        example = self.load_json("example_guardrail")["data"]
        manifest = Manifest.model_validate(example)
        self.assertIs(to_manifest(manifest), manifest)
        self.assertEqual(to_manifest(SAMGuardrail.model_validate(example)).kind, "Guardrail")
        self.assertEqual(to_manifest(example).kind, "Guardrail")
        self.assertEqual(to_manifest(manifest.to_yaml()).kind, "Guardrail")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "guardrail.json"
            path.write_text(json.dumps(example), encoding="utf-8")
            self.assertEqual(to_manifest(path).kind, "Guardrail")
            self.assertEqual(to_manifest(str(path)).kind, "Guardrail")
        with self.assertRaises(SmarterValueError):
            to_manifest(42)  # type: ignore[arg-type]

    def test_resource_id(self):
        """An id is a single path segment."""
        self.assertEqual(resource_id(5), "5")
        self.assertEqual(resource_id(" rMTAwMDAwNQx "), "rMTAwMDAwNQx")
        for value in ("", "a/b"):
            with self.subTest(value=value), self.assertRaises(SmarterValueError):
                resource_id(value)
