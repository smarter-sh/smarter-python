"""
Test that the SDK's mirrors of the platform's api contracts are current.

``tests/data/contracts/`` holds the platform's published JSON Schemas and examples (see
``scripts/sync-contracts.sh``). A field that the platform adds to a contract, and that the SDK's
model doesn't declare yet, fails :meth:`TestContracts.test_models_declare_every_field`.
"""

import json
import unittest
from pathlib import Path

from pydantic import BaseModel

from smarter.models import chat, journal

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
