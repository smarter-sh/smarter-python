"""
Test that the SDK's mirrors of the platform's api contracts are current.

``tests/data/contracts/`` holds the platform's published JSON Schemas and examples, and the cli
api's OpenAPI document (see ``scripts/sync-contracts.sh``). A field that the platform adds to a
contract, and that the SDK's model doesn't declare yet, fails
:meth:`TestContracts.test_models_declare_every_field`. A cli request of the SDK that the platform
doesn't publish, or a cli operation that the platform adds and the SDK doesn't call yet, fails
:class:`TestOpenApiContract`.
"""

import json
import re
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from pydantic import BaseModel
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from smarter.core.exceptions import SmarterError
from smarter.models import chat, journal

from .base import SmarterTestBase

CONTRACTS = Path(__file__).resolve().parent / "data" / "contracts"


def load(name: str) -> dict:
    """A contract file."""
    return json.loads((CONTRACTS / name).read_text(encoding="utf-8"))


def is_model(value: object) -> bool:
    """
    True for a Pydantic model class.

    On Python 3.10, a generic alias such as ``list[int]`` is an instance of ``type``, but not a
    valid argument of ``issubclass()``.
    """
    try:
        return isinstance(value, type) and issubclass(value, BaseModel)
    except TypeError:
        return False


def mirrored(module) -> dict[str, type[BaseModel]]:
    """The models of a module that mirror a platform contract model of the same name."""
    return {
        name: value
        for name, value in vars(module).items()
        if is_model(value) and name.startswith(("PromptChatApi", "SAMJournalApi"))
    }


class TestContracts(unittest.TestCase):
    """Test the chat and journal contract mirrors against the platform's schemas and examples."""

    def assert_declares_schema_fields(self, schema: dict, models: dict[str, type[BaseModel]]) -> int:
        """Assert that each mirrored model declares every property of its platform definition."""
        checked = 0
        for name, definition in schema["$defs"].items():
            model = models.get(name)
            if model is None:
                continue
            fields = {field.alias or key for key, field in model.model_fields.items()} | set(model.model_fields)
            with self.subTest(model=name):
                missing = set(definition.get("properties", {})) - fields
                self.assertFalse(missing, f"{name} does not declare the platform's fields {sorted(missing)}")
            checked += 1
        return checked

    def test_models_declare_every_field(self):
        """Every mirrored model declares every field of the platform's schema."""
        self.assertGreater(self.assert_declares_schema_fields(load("chat-contract.schema.json"), mirrored(chat)), 30)
        self.assertGreaterEqual(
            self.assert_declares_schema_fields(load("journal-contract.schema.json"), mirrored(journal)), 4
        )

    def test_examples_parse(self):
        """The platform's example of every version 2 contract model parses as the SDK's model."""
        examples = load("chat-contract.example.json")
        models = mirrored(chat)
        parsed = 0
        for name, example in examples.items():
            if name.endswith("V1"):
                continue
            with self.subTest(model=name):
                self.assertIn(name, models)
                models[name].model_validate(example)
                parsed += 1
        self.assertGreaterEqual(parsed, 8)


class TestOpenApiContract(SmarterTestBase):
    """Test the SDK's requests against the platform's OpenAPI document, for the api families that it covers."""

    NOT_CALLED = {
        "prompt",
        "prompt_config",
        "llmclient_plugin_retrieve",
        "llmclient_apikey_retrieve",
        "llmclient_customdomain_retrieve",
        "llmclient_function_retrieve",
    }
    """
    The operations that the SDK doesn't call: the cli's prompt commands, which it replaces with the chat api,.

    and the reads of a single related row of an LLMClient, whose lists it reads instead.
    """

    def setUp(self):
        super().setUp()
        self.document = load("openapi.json")

    def operation(self, method: str, path: str) -> str:
        """The operationId of a request, from the document's path templates, or fail."""
        for template, item in self.document["paths"].items():
            pattern = "^/api/v1" + re.sub(r"\\{[^/]+\\}", "[^/]+", re.escape(template)) + "$"
            if re.match(pattern, path) and method.lower() in item:
                return item[method.lower()]["operationId"]
        self.fail(f"{method} {path} is not in the platform's OpenAPI document.")

    def test_requests_are_published(self):
        """Every request of the SDK to a documented family is an operation, and the SDK calls every operation."""
        manifest = json.loads((CONTRACTS.parent / "sam" / "Guardrail.example.json").read_text(encoding="utf-8"))
        directory = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.addCleanup(directory.cleanup)
        upload = Path(directory.name) / "notes.txt"
        upload.write_text("Some notes.", encoding="utf-8")
        calls = [
            lambda: self.client.manifests.apply(manifest),
            lambda: self.client.manifests.validate(manifest),
            lambda: self.client.manifests.get("Guardrail"),
            lambda: self.client.manifests.describe("Guardrail", "example"),
            lambda: self.client.manifests.delete("Guardrail", "example"),
            lambda: self.client.manifests.deploy("LLMClient", "example"),
            lambda: self.client.manifests.undeploy("LLMClient", "example"),
            lambda: self.client.manifests.logs("LLMClient", "example"),
            lambda: self.client.manifests.example_manifest("Guardrail"),
            lambda: self.client.manifests.json_schema("Guardrail"),
            self.client.whoami,
            self.client.version,
            self.client.status,
            self.client.kinds,
            lambda: self.client.llm_clients.list(),
            lambda: self.client.llm_clients.retrieve("rMTAwMDAxMgx"),
            lambda: self.client.llm_clients.plugins(12),
            lambda: self.client.llm_clients.functions(12),
            lambda: self.client.llm_clients.api_keys(12),
            lambda: self.client.llm_clients.custom_domains(12),
            lambda: self.client.guardrails.list(),
            lambda: self.client.guardrails.retrieve("rMTAwMDAwMQx"),
            lambda: self.client.guardrails.evaluate(1, "hello"),
            lambda: self.client.guardrails.events(1, reviewed=False),
            lambda: self.client.secrets.list(),
            lambda: self.client.secrets.retrieve(1),
            lambda: self.client.mcp_clients.list(),
            lambda: self.client.mcp_clients.retrieve("rMTAwMDAwMQx"),
            lambda: self.client.mcp_clients.tools(1, refresh=True),
            lambda: self.client.mcp_clients.refresh(1),
            lambda: self.client.mcp_clients.call_tool(1, "add_numbers", {"a": 1, "b": 2}),
            lambda: self.client.vectorstores.list(),
            lambda: self.client.vectorstores.retrieve("rMTAwMDAwMQx"),
            lambda: self.client.vectorstores.status(1),
            lambda: self.client.vectorstores.deploy(1),
            lambda: self.client.vectorstores.undeploy(1),
            lambda: self.client.vectorstores.documents(1),
            lambda: self.client.vectorstores.add_text(1, "Some text.", name="faq"),
            lambda: self.client.vectorstores.add_url(1, "https://example.com/page.html"),
            lambda: self.client.vectorstores.add_files(1, [upload]),
            lambda: self.client.vectorstores.delete_document(1, 2),
            lambda: self.client.vectorstores.search(1, "query"),
            lambda: self.client.vectorstores.snapshots(1),
            lambda: self.client.vectorstores.create_snapshot(1),
            lambda: self.client.vectorstores.restore(1, 3),
            lambda: self.client.llm_clients.config(12),
            lambda: self.client.llm_clients.prompt("rMTAwMDAxMgx", "Hello"),
            lambda: list(self.client.llm_clients.stream(12, "Hello").__enter__()),
        ]
        for call in calls:
            try:
                call()
            except SmarterError:
                pass  # the requests are answered with 404s: only their paths matter.
        self.assertEqual(len(self.requests), len(calls))
        called = {self.operation(request.method, request.url.path) for request in self.requests}
        published = {
            item[method]["operationId"]
            for item in self.document["paths"].values()
            for method in ("get", "post", "delete")
            if method in item
        }
        self.assertEqual(
            published - called, self.NOT_CALLED, "The platform publishes cli operations that the SDK doesn't call."
        )


class TestRecordedResponses(unittest.TestCase):
    """
    Test that the responses that the SDK's tests replay, recorded from a real platform, are valid under the platform's OpenAPI document.

    A fixture that drifts from what the platform publishes would let the SDK's tests pass against a
    response that the platform never sends.
    """

    URI = "urn:smarter:openapi"

    FIXTURES = {
        "llmclients": ("/llm-clients/", "get"),
        "llmclient": ("/llm-clients/{id}/", "get"),
        "llmclient_plugins": ("/llm-clients/{id}/plugins/", "get"),
        "llmclient_functions": ("/llm-clients/{id}/functions", "get"),
        "config": ("/llm-clients/{id}/config/", "post"),
        "prompt": ("/llm-clients/{id}/prompt/", "post"),
        "guardrails": ("/guardrails/", "get"),
        "guardrail_eval": ("/guardrails/{id}/evaluate/", "post"),
        "guardrail_events": ("/guardrails/{id}/events/", "get"),
        "secrets": ("/secrets/", "get"),
        "mcpclients": ("/mcpclients/", "get"),
        "mcp_tools": ("/mcpclients/{id}/tools/", "get"),
        "vectorstores": ("/vectorstores/", "get"),
    }
    """Each fixture of tests/data/, by name, and the operation whose 200 response it is."""

    def test_fixtures_are_valid(self):
        document = load("openapi.json")
        registry = Registry().with_resource(
            self.URI, Resource.from_contents(document, default_specification=DRAFT202012)
        )
        for name, (path, method) in self.FIXTURES.items():
            with self.subTest(fixture=name):
                schema = document["paths"][path][method]["responses"]["200"]["content"]["application/json"]["schema"]
                schema = json.loads(json.dumps(schema).replace('"#/components/', f'"{self.URI}#/components/'))
                body = json.loads((CONTRACTS.parent / f"{name}.json").read_text(encoding="utf-8"))
                errors = [
                    f"{list(error.absolute_path)}: {error.message[:200]}"
                    for error in Draft202012Validator(schema, registry=registry).iter_errors(body)
                ]
                self.assertEqual(errors, [])
