"""Test smarter.resources.llmclients."""

import json

import httpx

from smarter import ResourceNotFoundError, SmarterError, SmarterPromptError
from smarter.core.exceptions import BadRequestError, SmarterValueError
from smarter.models.chat import PromptChatApiMessage
from smarter.resources.llmclients import request_messages, to_messages

from .base import SmarterTestBase


def sse(*events: tuple[str, object]) -> str:
    """The text of a Server-Sent Events stream."""
    return "".join(f"event: {name}\ndata: {json.dumps(data)}\n\n" for name, data in events)


class TestLLMClients(SmarterTestBase):
    """Test LLMClients."""

    def setUp(self):
        super().setUp()
        self.prompt_response = self.load_json("prompt")

    def test_list_retrieve_find(self):
        """LLMClients are listed, retrieved by id or hashed id, and found by name."""
        self.route("GET", "llm-clients/", fixture="llmclients")
        self.route("GET", "llm-clients/5/", fixture="llmclient")
        self.route("GET", "llm-clients/rMTAwMDAwNQx/", fixture="llmclient")
        llmclients = self.client.llm_clients.list()
        self.assertEqual(len(llmclients), 2)
        self.assertEqual(self.client.llm_clients.retrieve(5).name, "calculator")
        self.assertEqual(self.client.llm_clients.retrieve("rMTAwMDAwNQx").name, "calculator")
        self.assertEqual(self.client.llm_clients.find(llmclients[1].name).id, llmclients[1].id)
        with self.assertRaises(ResourceNotFoundError):
            self.client.llm_clients.find("nope")

    def test_tools(self):
        """An LLMClient's MCPClients, guardrails, and tools: its extensions, plugins, MCPClients and guardrails."""
        self.route("GET", "llm-clients/", fixture="llmclients")
        self.route("GET", "llm-clients/5/", fixture="llmclient")
        llmclient = self.client.llm_clients.retrieve(5)
        self.assertEqual(llmclient.mcpclients, [])
        self.assertEqual(llmclient.guardrails, [])
        self.assertEqual(
            [(tool.id, tool.name, tool.kind) for tool in llmclient.tools], [(1, "calculator", "Extension")]
        )
        self.assertEqual(
            [[tool.kind for tool in llmclient.tools] for llmclient in self.client.llm_clients.list()],
            [["Plugin"], ["Plugin"]],
        )

    def test_tools_default_to_empty(self):
        """An LLMClient from a platform that predates the tools has none, rather than failing to validate."""
        data = self.load_json("llmclient")
        for key in ("mcpclients", "guardrails", "tools"):
            del data[key]
        self.route("GET", "llm-clients/5/", json_body=data)
        llmclient = self.client.llm_clients.retrieve(5)
        self.assertEqual((llmclient.mcpclients, llmclient.guardrails, llmclient.tools), ([], [], []))

    def test_children(self):
        """An LLMClient's plugins, extensions, api keys and custom domains."""
        self.route("GET", "llm-clients/1/plugins/", fixture="llmclient_plugins")
        self.route("GET", "llm-clients/5/extensions", fixture="llmclient_extensions")
        api_key_id = "0b8e1c55-2f3a-4c1d-9a51-7d2f4e6b8a90"
        self.route("GET", "llm-clients/5/apikeys/", json_body=[{"id": 1, "llmclient": 5, "apiKey": api_key_id}])
        self.route(
            "GET",
            "llm-clients/5/customdomains",
            json_body=[{"id": 3, "name": "example_com", "domainName": "example.com", "verificationStatus": "Failed"}],
        )
        self.assertEqual(self.client.llm_clients.plugins(1)[0].plugin_meta.plugin_class, "sql")
        extension = self.client.llm_clients.extensions(5)[0]
        self.assertEqual((extension.name, extension.extension), ("calculator", 1))
        self.assertEqual(self.client.llm_clients.api_keys(5)[0].api_key, api_key_id)
        domain = self.client.llm_clients.custom_domains(5)[0]
        self.assertEqual((domain.domain_name, domain.verification_status), ("example.com", "Failed"))

    def test_config(self):
        """Config() starts or resumes a chat session."""
        self.route("POST", "llm-clients/5/config/", fixture="config")
        config = self.client.llm_clients.config(5, session_key="abc")
        self.assertEqual(config.llmclient.name, "calculator")
        self.assertEqual(config.extensions.meta_data.total_extensions, 1)
        self.assertEqual([(e.name, e.enabled) for e in config.extensions.extensions], [("calculator", True)])
        self.assertEqual(self.request_json(), {"session_key": "abc"})
        self.assertNotIn("verbose", self.last_request.url.params)

    def test_config_verbose(self):
        """Config(verbose=True) asks for the complete configuration, with the lists and the tool calls."""
        self.route("POST", "llm-clients/5/config/", fixture="config")
        config = self.client.llm_clients.config(5, verbose=True)
        self.assertEqual(self.last_request.url.params["verbose"], "true")
        self.assertEqual(self.request_json(), {"session_key": None})
        self.assertEqual(config.history.prompt_tool_call_history, [])
        self.assertFalse(config.meta_data.is_custom_domain)
        self.assertFalse(config.meta_data.is_authentication_required)

    def test_config_short(self):
        """Without verbose, the configuration has the counts of the plugins and extensions, and no lists."""
        response = self.load_json("config")
        data = response["data"]
        data["meta_data"] = {
            "ready": True,
            "is_deployed": False,
            "is_custom_domain": False,
            "is_authentication_required": True,
        }
        data["plugins"] = {"meta_data": {"total_plugins": 2, "plugins_returned": 0}}
        data["extensions"] = {"meta_data": {"total_extensions": 1, "extensions_returned": 0}}
        data["llmclient"]["total_tools"] = 3
        del data["history"]["prompt_tool_call_history"]
        self.route("POST", "llm-clients/5/config/", json_body=response)
        config = self.client.llm_clients.config(5)
        self.assertNotIn("verbose", self.last_request.url.params)
        self.assertEqual((config.plugins.meta_data.total_plugins, config.plugins.plugins), (2, []))
        self.assertEqual((config.extensions.meta_data.total_extensions, config.extensions.extensions), (1, []))
        self.assertEqual(config.llmclient.total_tools, 3)
        self.assertIsNone(config.history.prompt_tool_call_history)
        self.assertTrue(config.meta_data.is_authentication_required)

    def test_prompt(self):
        """Prompt() sends the user's message, and returns the LLM's reply."""
        self.route("POST", "llm-clients/5/prompt/", json_body=self.prompt_response)
        response = self.client.llm_clients.prompt(5, "What is 17 times 23?", session_key="k")
        self.assertTrue(response.text)
        self.assertEqual(
            self.request_json(),
            {"session_key": "k", "messages": [{"role": "user", "content": "What is 17 times 23?"}]},
        )

    def test_prompt_failure(self):
        """A failed prompt raises the LLM provider's status, with the error response as its body."""
        error = {"errorClass": "LLMProviderError", "description": "bad request", "status": 400}
        self.route("POST", "llm-clients/5/prompt/", status=400, json_body={**self.prompt_response, "error": error})
        with self.assertRaises(BadRequestError) as context:
            self.client.llm_clients.prompt(5, "hi")
        self.assertEqual(context.exception.message, "bad request")

    def test_request_messages(self):
        """Smarter's own messages are not sent, and every message keeps its content key."""
        thread = to_messages(
            [
                {"role": "system", "content": "be brief"},
                {"role": "assistant", "tool_calls": [{"id": "c", "function": {"name": "f", "arguments": "{}"}}]},
                {"role": "smarter", "content": "charges"},
                PromptChatApiMessage(role="tool", content="1", tool_call_id="c"),
            ]
        )
        sent = request_messages(thread)
        self.assertEqual([message["role"] for message in sent], ["system", "assistant", "tool"])  # type: ignore[index]
        self.assertIn("content", sent[1])  # type: ignore[operator]
        self.assertIsNone(sent[1]["content"])  # type: ignore[index]

    def test_stream(self):
        """A stream yields the progress events, then has the prompt's response."""
        self.route("POST", "llm-clients/5/prompt/", text=self.load_text("prompt_sse.txt"))
        with self.client.llm_clients.stream(5, "hi") as stream:
            events = list(stream)
        self.assertTrue(events)
        self.assertEqual(events[0].type, "llm_request")
        self.assertEqual(stream.result.status, 200)  # type: ignore[union-attr]
        self.assertTrue(stream.response.text)

    def test_stream_until_done(self):
        """``until_done()`` reads the stream, without a with statement, and returns the response."""
        self.route("POST", "llm-clients/5/prompt/", text=self.load_text("prompt_sse.txt"))
        stream = self.client.llm_clients.stream(5, "hi")
        try:
            self.assertTrue(stream.until_done().text)
        finally:
            stream.__exit__(None, None, None)

    def test_stream_errors(self):
        """A stream that failed, or that hasn't been read, raises when its response is read."""
        error = {"errorClass": "LLMProviderError", "description": "boom", "status": 400}
        failed = {**self.prompt_response, "error": error}
        error_only = {"error": {"errorClass": "NotFound", "description": "gone", "status": 404}}
        for body, message in ((failed, "boom"), (error_only, "gone")):
            with self.subTest(message=message):
                self.route("POST", "llm-clients/5/prompt/", text=sse(("result", {"status": 400, "response": body})))
                with self.client.llm_clients.stream(5, "hi") as stream:
                    with self.assertRaises(SmarterPromptError) as context:
                        stream.until_done()
                self.assertEqual(str(context.exception), message)
        with self.assertRaises(SmarterError):
            _ = self.client.llm_clients.stream(5, "hi").response


class TestChatSession(SmarterTestBase):
    """Test ChatSession."""

    def setUp(self):
        super().setUp()
        self.route("POST", "llm-clients/5/config/", fixture="config")
        self.prompt_response = self.load_json("prompt")
        self.config = self.load_json("config")["data"]

    def test_new_session(self):
        """A new session's thread is the LLMClient's system prompt and welcome message."""
        chat = self.client.llm_clients.chat(5)
        self.assertEqual(chat.session_key, self.config["session_key"])
        self.assertEqual([message.role for message in chat.messages][:1], ["system"])

    def test_resumed_session(self):
        """A resumed session's thread is its history."""
        config = json.loads(json.dumps(self.config))
        config["history"]["chat_history"] = [{"role": "user", "content": "earlier"}]
        self.route("POST", "llm-clients/5/config/", json_body={"api": "smarter.sh/v1", "data": config})
        chat = self.client.llm_clients.chat(5, session_key=config["session_key"])
        self.assertEqual(chat.messages[0].text, "earlier")

    def test_introduction_without_prompts(self):
        """An LLMClient without a system prompt or welcome message starts with an empty thread."""
        config = json.loads(json.dumps(self.config))
        config["llmclient"]["default_system_role"] = None
        config["llmclient"]["app_welcome_message"] = None
        self.route("POST", "llm-clients/5/config/", json_body={"api": "smarter.sh/v1", "data": config})
        self.assertEqual(self.client.llm_clients.chat(5).messages, [])

    def test_send(self):
        """Send() sends the thread with the session key, and adds the prompt's messages to it."""
        self.route("POST", "llm-clients/5/prompt/", json_body=self.prompt_response)
        chat = self.client.llm_clients.chat(5)
        before = len(chat.messages)
        response = chat.send("What is 17 times 23?")
        body = self.request_json()
        self.assertEqual(body["session_key"], chat.session_key)  # type: ignore[index]
        self.assertEqual(body["messages"][-1], {"role": "user", "content": "What is 17 times 23?"})  # type: ignore[index]
        self.assertEqual(len(chat.messages), before + 1 + len(response.data.messages))
        chat.send({"role": "user", "content": "again"})
        self.assertEqual(self.request_json()["messages"][-1]["content"], "again")  # type: ignore[index]

    def test_stream(self):
        """A chat stream updates the thread when it succeeds, and not when it fails."""
        self.route("POST", "llm-clients/5/prompt/", text=self.load_text("prompt_sse.txt"))
        chat = self.client.llm_clients.chat(5)
        before = len(chat.messages)
        with chat.stream("hi") as stream:
            list(stream)
        self.assertGreater(len(chat.messages), before + 1)
        count = len(chat.messages)
        failed = {"error": {"errorClass": "NotFound", "description": "gone", "status": 404}}

        def handler(_request):
            return httpx.Response(200, text=sse(("result", {"status": 404, "response": failed})))

        self.route("POST", "llm-clients/5/prompt/", handler=handler)
        with chat.stream({"role": "user", "content": "again"}) as stream:
            list(stream)
        self.assertEqual(len(chat.messages), count)

    def test_deploy(self):
        """Deploy() and undeploy() go through the manifest api."""
        self.route("POST", "cli/deploy/LLMClient/", json_body={"message": "deployed"})
        self.route("POST", "cli/undeploy/LLMClient/", json_body={"message": "undeployed"})
        self.assertEqual(self.client.llm_clients.deploy("calculator").message, "deployed")
        self.assertEqual(self.client.llm_clients.undeploy("calculator").message, "undeployed")

    def test_apply_checks_kind(self):
        """A resource's apply() refuses a manifest of another kind."""
        with self.assertRaises(SmarterValueError):
            self.client.llm_clients.apply(self.load_json("example_guardrail")["data"])
