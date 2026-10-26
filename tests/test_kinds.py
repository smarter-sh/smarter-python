"""
Test smarter.models.kinds: the SDK's SAMKinds is smarter-types' own.

smarter-types tests SAMKinds itself, apply order included. These tests check what only the SDK can:
that its kinds are the kinds whose JSON Schemas the platform publishes.
"""

import json
import unittest
from pathlib import Path

import smarter_types

from smarter import SAMKinds as TopLevelSAMKinds
from smarter.models.kinds import SAMKinds

SAM_DATA = Path(__file__).resolve().parent / "data" / "sam"


class TestSAMKinds(unittest.TestCase):
    """Test SAMKinds against the platform's committed schemas."""

    def test_is_smarter_types(self):
        """The SDK re-exports smarter-types' SAMKinds, from the top-level package too."""
        self.assertIs(SAMKinds, smarter_types.SAMKinds)
        self.assertIs(TopLevelSAMKinds, SAMKinds)

    def test_a_member_of_every_schema(self):
        """There is a member of every kind whose schema the platform publishes, and only of those."""
        kinds = {path.name.split(".")[0] for path in SAM_DATA.glob("*.schema.json")}
        self.assertEqual(set(SAMKinds.all()), kinds)

    def test_examples_have_a_member(self):
        """Every example manifest's kind is a member, and has a place in the apply order."""
        for path in SAM_DATA.glob("*.example.json"):
            with self.subTest(path=path.name):
                kind = json.loads(path.read_text(encoding="utf-8"))["kind"]
                self.assertEqual(SAMKinds(kind).value, kind)
                self.assertLess(SAMKinds.apply_rank(kind), len(SAMKinds.apply_order()))


if __name__ == "__main__":
    unittest.main()
