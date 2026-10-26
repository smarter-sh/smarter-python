"""Test smarter.models: the base models, manifests, chat helpers and the React contract."""

import json
import tempfile
import unittest
from pathlib import Path

from smarter.core.exceptions import SmarterValueError
from smarter.models.base import SmarterResource
from smarter.models.chat import (
    PromptChatApiMessage,
    PromptChatApiPromptResponse,
    PromptChatApiPromptResult,
)
from smarter.models.manifest import KindInfo, Manifest, ManifestList
from smarter.models.react import ReactAppAssets, ViteManifest
from smarter.models.sam import SAMLLMClient

from .base import SmarterTestBase


class TestBaseModels(unittest.TestCase):
    """Test SmarterModel and SmarterResource."""

    def test_camel_case_and_extra_fields(self):
        """A resource reads camelCase fields, keeps unknown ones, and dumps the api's names."""
        resource = SmarterResource.model_validate({"id": 1, "name": "a", "hashedId": "h", "newField": 2})
        self.assertEqual(resource.hashed_id, "h")
        self.assertEqual(resource.model_extra, {"newField": 2})
        self.assertEqual(resource.to_dict()["hashedId"], "h")
        self.assertEqual(json.loads(resource.to_json(indent=None))["newField"], 2)


class TestManifest(unittest.TestCase):
    """Test Manifest and ManifestList."""

    def test_from_yaml(self):
        """YAML and JSON text parse, and anything else is a SmarterValueError."""
        manifest = Manifest.from_yaml("apiVersion: smarter.sh/v1\nkind: Secret\nmetadata:\n  name: s\nspec: {}\n")
        self.assertEqual(manifest.kind, "Secret")
        self.assertEqual(Manifest.from_yaml(json.dumps(manifest.model_dump())).metadata.name, "s")
        for text in ("- a list", "key: [unclosed"):
            with self.subTest(text=text), self.assertRaises(SmarterValueError):
                Manifest.from_yaml(text)

    def test_unquoted_dates(self):
        """An unquoted date or time in the YAML is kept as its ISO 8601 string."""
        text = (
            "apiVersion: smarter.sh/v1\nkind: LLMClient\n"
            "metadata:\n  name: x\n  annotations:\n    - example.com/release-date: 2024-06-15\n"
            "spec:\n  config:\n    at: 2024-06-15 10:30:00\n    sizes: [2024-01-01]\n"
        )
        manifest = Manifest.from_yaml(text)
        self.assertEqual(manifest.metadata.annotations, [{"example.com/release-date": "2024-06-15"}])
        self.assertEqual(manifest.spec["config"], {"at": "2024-06-15T10:30:00", "sizes": ["2024-01-01"]})

    def test_from_file_and_to_yaml(self):
        """A manifest round-trips through a YAML file, without its status."""
        manifest = Manifest.model_validate(SmarterTestBase.load_json("describe_llmclient")["data"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "llmclient.yaml"
            path.write_text(manifest.to_yaml(), encoding="utf-8")
            loaded = Manifest.from_file(path)
        self.assertIsNone(loaded.status)
        self.assertEqual(loaded.spec, manifest.spec)

    def test_to_sam(self):
        """A described manifest becomes its kind's typed model, and an unknown kind is an error."""
        manifest = Manifest.model_validate(SmarterTestBase.load_json("describe_llmclient")["data"])
        typed = manifest.to_sam()
        self.assertIsInstance(typed, SAMLLMClient)
        self.assertEqual(typed.status.recordLocator, manifest.status["recordLocator"])  # type: ignore[index,union-attr]
        with self.assertRaises(SmarterValueError):
            Manifest(kind="Nope", metadata={"name": "x"}).to_sam()  # type: ignore[arg-type]

    def test_manifest_list(self):
        """A get result's rows and names."""
        result = ManifestList.model_validate(SmarterTestBase.load_json("get_llmclient")["data"])
        self.assertEqual(len(result.items), 2)
        self.assertEqual(len(result.names), 2)
        users = ManifestList(kind="User", data={"items": [{"username": "u"}, {"id": 1}]})  # type: ignore[arg-type]
        self.assertEqual(users.names, ["u"])

    def test_kind_info(self):
        """A kind is read from the platform's PascalCase keys."""
        kind = KindInfo.model_validate(SmarterTestBase.load_json("resources")["data"][0])
        self.assertEqual(kind.api_kind, "Plugin")
        self.assertFalse(kind.deployable)


class TestChatModels(unittest.TestCase):
    """Test the chat contract's helpers."""

    def test_message_text(self):
        """A message's text, from a string or from its text parts."""
        self.assertEqual(PromptChatApiMessage(role="user", content="hi").text, "hi")
        self.assertEqual(PromptChatApiMessage(role="assistant").text, "")
        parts = PromptChatApiMessage.model_validate(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "a"},
                    {"type": "image_url", "image_url": {"url": "data:,"}},
                    {"type": "text", "text": "b"},
                ],
            }
        )
        self.assertEqual(parts.text, "a\n\nb")

    def test_response_text(self):
        """A prompt's text is the last assistant message with content."""
        response = PromptChatApiPromptResponse.model_validate(SmarterTestBase.load_json("prompt"))
        self.assertTrue(response.text)
        self.assertTrue(response.data.assistant_messages)
        self.assertEqual(PromptChatApiPromptResult(status=200).text, "")


class TestReactModels(unittest.TestCase):
    """Test the Django-React integration contract."""

    MANIFEST = {
        "index.html": {"file": "assets/index.js", "isEntry": True, "imports": ["_x.js", "_y.js"], "css": ["a.css"]},
        "_x.js": {"file": "assets/x.js", "imports": ["index.html"], "css": ["b.css"]},
        "_custom": {"buildTime": "2026-10-12T01:09:47.988Z", "version": "0.3.0", "buildEnv": "production"},
    }

    def test_vite_manifest(self):
        """A manifest.json's entry point and assets, in order, and its build information."""
        manifest = ViteManifest.model_validate(self.MANIFEST)
        self.assertTrue(manifest)
        self.assertEqual(manifest.entry_key(), "index.html")
        self.assertEqual(manifest.collect_assets("index.html", "js"), ["assets/index.js", "assets/x.js"])
        self.assertEqual(manifest.collect_assets("index.html", "css"), ["a.css", "b.css"])
        self.assertEqual(manifest.build_info.version, "0.3.0")  # type: ignore[union-attr]
        self.assertEqual(set(manifest.model_dump(by_alias=True)), {"index.html", "_x.js", "_custom"})
        self.assertEqual(ReactAppAssets(js=["a.js"]).css, [])

    def test_empty_manifest(self):
        """A manifest without chunks is falsy, and has no entry point."""
        manifest = ViteManifest.model_validate({})
        self.assertFalse(manifest)
        self.assertIsNone(manifest.entry_key())
        self.assertEqual(ViteManifest(chunks={}).model_dump(), {})
