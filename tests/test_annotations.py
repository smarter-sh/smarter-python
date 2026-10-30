"""Test smarter.models.annotations: SAM annotations, their legacy list form, and annotation selectors."""

import unittest
from datetime import date

from pydantic import ValidationError

from smarter.models.annotations import (
    annotation_selector,
    annotation_value,
    normalize_annotations,
)
from smarter.models.chat import PromptChatApiPluginMeta
from smarter.models.manifest import Manifest, ManifestMetadata
from smarter.models.sam import SAMGuardrail

from .test_sam import example


class TestAnnotationValue(unittest.TestCase):
    """Test annotation_value()."""

    def test_values(self):
        """Every value becomes the string that the platform stores."""
        cases = [
            ("text", "text"),
            (None, ""),
            (True, "true"),
            (False, "false"),
            (42, "42"),
            (1.5, "1.5"),
            (date(2024, 6, 15), "2024-06-15"),
            ([1, "a"], '[1, "a"]'),
            ({"a": 1}, '{"a": 1}'),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(annotation_value(value), expected)


class TestNormalizeAnnotations(unittest.TestCase):
    """Test normalize_annotations()."""

    def test_map(self):
        """A map keeps its keys and order, with string values."""
        self.assertEqual(
            normalize_annotations({"acme.com/b": "x", "acme.com/a": 1}), {"acme.com/b": "x", "acme.com/a": "1"}
        )

    def test_legacy_list(self):
        """The list of one-key maps becomes a map, and a repeated key's last value wins."""
        self.assertEqual(
            normalize_annotations([{"acme.com/a": True}, {"acme.com/b": "x"}, {"acme.com/a": "y"}]),
            {"acme.com/a": "y", "acme.com/b": "x"},
        )
        self.assertEqual(normalize_annotations([]), {})

    def test_none_and_other_values(self):
        """None is an empty map, another value is left for Pydantic, and a list of non-maps is an error."""
        self.assertEqual(normalize_annotations(None), {})
        self.assertEqual(normalize_annotations("text"), "text")
        with self.assertRaises(ValueError):
            normalize_annotations(["acme.com/a"])


class TestAnnotationSelector(unittest.TestCase):
    """Test annotation_selector()."""

    def test_selector(self):
        """A requirement or a list of them becomes a list, without blank requirements."""
        self.assertEqual(annotation_selector(None), [])
        self.assertEqual(annotation_selector(" acme.com/a=1 "), ["acme.com/a=1"])
        self.assertEqual(annotation_selector(["acme.com/a", " ", "!acme.com/b"]), ["acme.com/a", "!acme.com/b"])
        self.assertEqual(annotation_selector(("acme.com/a!=1",)), ["acme.com/a!=1"])


class TestModelsWithAnnotations(unittest.TestCase):
    """Test the models whose fields are annotations."""

    def test_manifest_metadata(self):
        """A manifest's annotations are a map, from either form, and invalid ones are rejected."""
        self.assertEqual(ManifestMetadata(name="x").annotations, {})
        legacy = ManifestMetadata.model_validate({"name": "x", "annotations": [{"acme.com/a": 1}]})
        self.assertEqual(legacy.annotations, {"acme.com/a": "1"})
        for invalid in (["acme.com/a"], "text"):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                ManifestMetadata.model_validate({"name": "x", "annotations": invalid})

    def test_sam_models(self):
        """A SAM model accepts the legacy list and unquoted scalars, as the platform does."""
        document = example("Guardrail")
        document["metadata"]["annotations"] = [{"acme.com/active": True}, {"acme.com/since": date(2024, 6, 15)}]
        guardrail = SAMGuardrail.model_validate(document)
        self.assertEqual(guardrail.metadata.annotations, {"acme.com/active": "true", "acme.com/since": "2024-06-15"})
        document["metadata"].pop("annotations")
        self.assertIsNone(SAMGuardrail.model_validate(document).metadata.annotations)
        manifest = Manifest.model_validate(example("Guardrail"))
        self.assertEqual(manifest.to_sam().metadata.annotations, manifest.metadata.annotations)

    def test_chat_plugin_meta(self):
        """A plugin's annotations in the chat contract are a map, or None."""
        meta = PromptChatApiPluginMeta.model_validate(
            {"id": 1, "name": "p", "plugin_class": "static", "annotations": [{"acme.com/a": "b"}]}
        )
        self.assertEqual(meta.annotations, {"acme.com/a": "b"})
        self.assertIsNone(PromptChatApiPluginMeta(id=1, name="p", plugin_class="static").annotations)


if __name__ == "__main__":
    unittest.main()
