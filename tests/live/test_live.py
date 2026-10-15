"""
Test the SDK against a running Smarter platform.

These tests are skipped unless ``SMARTER_TEST_LIVE=true``. They read the client's configuration
as the SDK always does (``SMARTER_API_KEY``, ``SMARTER_BASE_URL``, ...), e.g.:

.. code-block:: console

    SMARTER_TEST_LIVE=true SMARTER_BASE_URL=http://localhost:9357 SMARTER_API_KEY=... \\
        python -m unittest discover -s tests/live -t .

They validate the SDK's models against the platform's real responses. They prompt an LLMClient,
which makes billable LLM requests, and they apply and delete a throwaway Guardrail. They never
deploy anything: deploy creates real, billable infrastructure.

``SMARTER_TEST_LLMCLIENT`` names the LLMClient to prompt (default ``calculator``, which the platform
creates as an example), and its built-in calculator function makes the prompt call a tool.
"""

import os
import unittest
import uuid

from smarter import APIStatusError, NotFoundError, ResourceNotFoundError, Smarter
from smarter.models.manifest import Manifest
from smarter.resources.catalog import PLUGIN_KINDS

LIVE = os.environ.get("SMARTER_TEST_LIVE", "").lower() == "true"
LLMCLIENT = os.environ.get("SMARTER_TEST_LLMCLIENT", "calculator")


@unittest.skipUnless(LIVE, "set SMARTER_TEST_LIVE=true to test against a running platform")
class TestLive(unittest.TestCase):
    """Test the SDK against a running platform."""

    client: Smarter

    @classmethod
    def setUpClass(cls):
        cls.client = Smarter()

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def test_platform(self):
        """Whoami, version, status and kinds parse."""
        self.assertTrue(self.client.whoami().user.username)
        self.assertTrue(self.client.version().api.version)
        self.client.status()
        kinds = {kind.api_kind for kind in self.client.kinds()}
        self.assertIn("LLMClient", kinds)

    def test_lists(self):
        """Every REST list parses."""
        for resource in (
            self.client.llm_clients,
            self.client.guardrails,
            self.client.mcp_clients,
            self.client.secrets,
            self.client.plugins,
            self.client.llm_hosts,
            self.client.orchestrators,
            self.client.vectorsearches,
            self.client.accounts,
        ):
            with self.subTest(resource=type(resource).__name__):
                resource.list()
        self.client.accounts.users.list()
        self.client.accounts.contacts.list()
        self.client.accounts.user_profiles.list()
        self.client.history.sessions()
        self.client.history.tool_calls()
        self.client.history.plugin_usage()

    def test_retrieves(self):
        """The first row of each list of the accounts and the prompt history is retrieved by its id."""
        for listed, retrieve in (
            (self.client.accounts.users.list, self.client.accounts.users.retrieve),
            (self.client.accounts.user_profiles.list, self.client.accounts.user_profiles.retrieve),
            (self.client.accounts.contacts.list, self.client.accounts.contacts.retrieve),
            (self.client.history.sessions, self.client.history.session),
            (self.client.history.tool_calls, self.client.history.tool_call),
            (self.client.history.plugin_usage, self.client.history.plugin_use),
        ):
            with self.subTest(retrieve=retrieve.__qualname__):
                rows = listed()
                if rows:
                    self.assertEqual(retrieve(rows[0].id).id, rows[0].id)

    def test_optional_apis(self):
        """The apis that a platform may disable, or that require a superuser, parse when they answer."""
        for name, call in (
            ("vectorstores", self.client.vectorstores.list),
            ("proxies", self.client.proxies.list),
            ("journal", self.client.journal.list),
            ("providers", self.client.providers.list),
        ):
            with self.subTest(api=name):
                try:
                    call()
                except (NotFoundError, ResourceNotFoundError) as e:
                    self.skipTest(f"{name} is not enabled: {e}")
                except APIStatusError as e:
                    self.skipTest(f"the platform's {name} api failed: {e}")

    def test_manifest_kinds(self):
        """
        Get, example_manifest and json_schema parse for every kind.

        A platform error is the platform's, not the SDK's, so it skips that kind's subtest with the
        platform's message. An SDK error, e.g. a response that doesn't match its model, fails it.
        """
        for kind in self.client.kinds():
            with self.subTest(kind=kind.api_kind):
                try:
                    self.client.manifests.get(kind.api_kind)
                except APIStatusError as e:
                    self.skipTest(f"the platform's get {kind.api_kind} failed: {e}")
                self.assertEqual(self.client.manifests.example_manifest(kind.api_kind).kind, kind.api_kind)
                self.assertIn("properties", self.client.manifests.json_schema(kind.api_kind))

    def test_sam_models(self):
        """A described resource of every kind parses as its kind's SAM model."""
        plugins = self.client.plugins.list()
        for kind in self.client.kinds():
            with self.subTest(kind=kind.api_kind):
                if kind.api_kind in PLUGIN_KINDS:
                    # the platform's get of a plugin kind returns every plugin, so they are picked by kind.
                    names = [plugin.name for plugin in plugins if plugin.kind == kind.api_kind]
                else:
                    try:
                        names = self.client.manifests.get(kind.api_kind).names
                    except APIStatusError as e:
                        self.skipTest(f"the platform's get {kind.api_kind} failed: {e}")
                if not names:
                    self.skipTest(f"there is no {kind.api_kind} to describe")
                try:
                    manifest = self.client.manifests.describe(kind.api_kind, names[0])
                except APIStatusError as e:
                    self.skipTest(f"the platform's describe {kind.api_kind} {names[0]} failed: {e}")
                # the platform returns some names with dashes in get, and underscores in describe.
                self.assertEqual(manifest.to_sam().metadata.name.replace("-", "_"), names[0].replace("-", "_"))

    def test_manifest_lifecycle(self):
        """A Guardrail is validated, applied, described, found, evaluated and deleted."""
        manifest = self.client.guardrails.example_manifest()
        name = f"sdk_live_test_{uuid.uuid4().hex[:8]}"
        manifest.metadata.name = name
        self.assertTrue(self.client.manifests.validate(manifest).valid)
        self.client.guardrails.apply(manifest)
        self.addCleanup(self.client.guardrails.delete, name)
        described = self.client.guardrails.describe(name)
        self.assertIsInstance(described, Manifest)
        self.assertEqual(described.metadata.name, name)
        self.assertEqual(self.client.manifests.get("Guardrail", name).names, [name])
        guardrail = self.client.guardrails.find(name)
        self.assertEqual(self.client.guardrails.retrieve(guardrail.id).name, name)
        stage = guardrail.stage or "input"
        evaluation = self.client.guardrails.evaluate(guardrail.id, "My SSN is 078-05-1120.", stage=stage)  # type: ignore[arg-type]
        self.assertEqual(evaluation.guardrail, name)
        self.client.guardrails.events(guardrail.id)

    def test_prompt(self):
        """A prompt returns the LLM's reply, and its tool call."""
        llmclient = self.client.llm_clients.find(LLMCLIENT)
        response = self.client.llm_clients.prompt(llmclient.id, "What is 17 times 23? Use the calculator.")
        self.assertIn("391", response.text.replace(",", ""))
        self.assertIn(("calculator", "Function"), [(tool.name, tool.kind) for tool in llmclient.tools])
        self.client.llm_clients.functions(llmclient.id)
        self.client.llm_clients.plugins(llmclient.id)
        self.client.llm_clients.api_keys(llmclient.id)
        self.client.llm_clients.custom_domains(llmclient.id)

    def test_stream_and_chat(self):
        """A chat keeps its session and thread, and a streamed prompt reports its progress."""
        llmclient = self.client.llm_clients.find(LLMCLIENT)
        chat = self.client.llm_clients.chat(llmclient.hashed_id or llmclient.id)
        self.assertIn("1024", chat.send("What is 2 to the 10th power? Use the calculator.").text.replace(",", ""))
        with chat.stream("Divide that by 4, with the calculator.") as stream:
            events = list(stream)
        self.assertTrue(any(event.type == "llm_request" for event in events))
        self.assertIn("256", stream.response.text)
        self.assertIn(stream.response.data.messages[-1], chat.messages)
        resumed = self.client.llm_clients.chat(llmclient.id, session_key=chat.session_key)
        self.assertEqual(resumed.session_key, chat.session_key)
        self.assertTrue(resumed.messages)

    def test_mcp_and_llmhosts(self):
        """The MCPClient tools and the LLMHost report parse."""
        mcpclients = self.client.mcp_clients.list()
        if mcpclients:
            self.client.mcp_clients.tools(mcpclients[0].id)
        llmhosts = self.client.llm_hosts.list()
        self.client.llm_hosts.report()
        if llmhosts:
            self.client.llm_hosts.status(llmhosts[0].id)
            self.client.llm_hosts.plan(llmhosts[0].id)


if __name__ == "__main__":
    unittest.main()
