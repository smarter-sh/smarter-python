"""Test smarter.resources.history."""

from .base import SmarterTestBase


class TestHistory(SmarterTestBase):
    """Test PromptHistory and Journal."""

    def test_prompt_history(self):
        """Sessions, tool calls and plugin uses are listed and retrieved."""
        self.route("GET", "prompts/history/prompt/", fixture="history")
        self.route("GET", "prompts/history/prompt/43/", json_body=self.load_json("history")[0])
        self.route("GET", "prompts/history/tool-calls/", fixture="toolcalls")
        self.route("GET", "prompts/history/tool-calls/3/", json_body=self.load_json("toolcalls")[0])
        self.route("GET", "prompts/history/plugin-usage/", fixture="plugin_usage")
        self.assertEqual(len(self.client.history.sessions()[0].session_key), 64)  # type: ignore[arg-type]
        self.assertEqual(self.client.history.session(43).llmclient, 5)
        tool_call = self.client.history.tool_calls()[0]
        self.assertEqual(tool_call.function_name, "calculator")
        self.assertEqual(tool_call.prompt.llmclient, 5)  # type: ignore[union-attr]
        self.assertEqual(self.client.history.tool_call(3).id, 3)
        usage = self.client.history.plugin_usage()[0]
        self.assertEqual(usage.prompt.llmclient, 5)  # type: ignore[union-attr]
        self.assertEqual(usage.plugin.kind, "WebsearchPlugin")  # type: ignore[union-attr]
        self.route("GET", "prompts/history/plugin-usage/4/", json_body=self.load_json("plugin_usage")[0])
        self.assertEqual(self.client.history.plugin_use(4).input_text, "What is 17 * 23?")

    def test_journal(self):
        """The journal is paged, and an entry is retrieved by key."""
        self.route("GET", "journal/", fixture="journal")
        page = self.client.journal.list(page=2, page_size=10, search="apply", ordering="-createdAt")
        self.assertEqual(page.pagination.page_size, 25)
        self.assertEqual(
            dict(self.last_request.url.params),
            {"page": "2", "page_size": "10", "search": "apply", "ordering": "-createdAt"},
        )
        key = "a" * 64
        entry = {
            "key": key,
            "thing": "Guardrail",
            "command": "apply",
            "statusCode": 200,
            "user": "admin",
            "request": {},
        }
        self.route("GET", f"journal/{key}/", json_body=entry)
        self.assertEqual(self.client.journal.retrieve(key).status_code, 200)
