"""Test smarter.core.streaming."""

import unittest

from smarter.core.streaming import ServerSentEvent, iter_sse

from .base import SmarterTestBase


class TestStreaming(unittest.TestCase):
    """Test the Server-Sent Events parser."""

    def test_platform_stream(self):
        """A real prompt stream parses into its progress events and its result."""
        lines = SmarterTestBase.load_text("prompt_sse.txt").splitlines()
        events = list(iter_sse(lines))
        self.assertEqual([event.event for event in events][-1], "result")
        self.assertTrue(all(event.event in ("progress", "result") for event in events))
        self.assertEqual(events[0].json()["type"], "llm_request")

    def test_fields(self):
        """Comments are skipped, multi-line data is joined, and id and retry are kept."""
        lines = [
            ": comment",
            "retry: 3000",
            "",
            "event: x",
            "id: 7",
            "retry: 10",
            "data: a",
            "data:b",
            "",
            "data: last",
        ]
        events = list(iter_sse(lines))
        self.assertEqual(events[0], ServerSentEvent(event="x", data="a\nb", id="7", retry=10))
        self.assertEqual(events[1], ServerSentEvent(event=None, data="last"))
        self.assertEqual(len(events), 2)

    def test_ignored_fields(self):
        """Unknown fields, and a retry that is not a number, are ignored."""
        events = list(iter_sse(["foo: bar", "retry: soon", "data: {}", ""]))
        self.assertEqual(events, [ServerSentEvent(event=None, data="{}")])
        self.assertEqual(events[0].json(), {})
