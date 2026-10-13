"""Test smarter.models.sam: the generated SAM models."""

import json
import unittest
from pathlib import Path

import yaml

from smarter.models.manifest import Manifest
from smarter.models.sam import SAM_MODELS, SAMGuardrail, SAMModel, sam_model

SAM_DATA = Path(__file__).resolve().parent / "data" / "sam"


def example(kind: str) -> dict:
    """The platform's example manifest of a kind."""
    return json.loads((SAM_DATA / f"{kind}.example.json").read_text(encoding="utf-8"))


class TestSAMModels(unittest.TestCase):
    """Test the generated SAM models against the platform's schemas and examples."""

    def test_a_model_of_every_schema(self):
        """There is a model of every kind whose schema was saved, and only of those."""
        kinds = {path.name.split(".")[0] for path in SAM_DATA.glob("*.schema.json")}
        self.assertEqual(set(SAM_MODELS), kinds)
        self.assertGreaterEqual(len(kinds), 20)

    def test_examples_parse(self):
        """Every kind's example manifest parses as its model, and keeps its kind and name."""
        for kind, model in SAM_MODELS.items():
            with self.subTest(kind=kind):
                manifest = model.model_validate(example(kind))
                self.assertEqual(manifest.kind, kind)
                self.assertEqual(manifest.metadata.name, example(kind)["metadata"]["name"])

    def test_sam_model(self):
        """A model is looked up by its kind."""
        self.assertIs(sam_model("Guardrail"), SAMGuardrail)
        with self.assertRaises(KeyError):
            sam_model("Nope")

    def test_round_trip(self):
        """A SAM model dumps as an applicable manifest, and as YAML with or without its status."""
        guardrail = SAMGuardrail.model_validate(example("Guardrail"))
        document = guardrail.to_manifest_dict()
        self.assertNotIn("status", document)
        self.assertEqual(Manifest.model_validate(document).to_sam(), guardrail.model_copy(update={"status": None}))
        self.assertNotIn("status:", guardrail.to_yaml())
        self.assertEqual(yaml.safe_load(guardrail.to_yaml(status=True))["kind"], "Guardrail")
        self.assertTrue(issubclass(SAMGuardrail, SAMModel))
