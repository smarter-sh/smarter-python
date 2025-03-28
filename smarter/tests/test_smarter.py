"""
top-level test file for the smarter package.
"""

import unittest

from smarter import Account, Chatbot, Plugin, Smarter
from smarter.common.classes import DEFAULT_API_ENDPOINT
from smarter.common.conf import settings as smarter_settings
from smarter.common.const import SmarterEnvironments


class TestApi(unittest.TestCase):
    """
    to verify that our codebase if free of syntax errors.
    """

    def test_settings(self):
        self.assertTrue(smarter_settings)
        self.assertEqual(smarter_settings.root_domain, "smarter.sh")
        self.assertEqual(smarter_settings.environment, SmarterEnvironments.PROD)

    def test_client(self):
        client = Smarter()
        self.assertTrue(client)
        self.assertEqual(client.base_url, "https://platform.smarter.sh/api/v1/")
        self.assertEqual(client.url_endpoint, DEFAULT_API_ENDPOINT)
        self.assertEqual(client.url, "https://platform.smarter.sh/api/v1/cli/whoami/")
        self.assertEqual(client.api_key, smarter_settings.smarter_api_key.get_secret_value())
        self.assertEqual(client.api, "smarter.sh/v1")
        self.assertEqual(client.thing, "None")
        self.assertIn("key", client.metadata)
        self.assertEqual(client.timeout, smarter_settings.smarter_default_http_timeout)

    def test_chatbot(self):
        chatbot = Chatbot(name="netec-demo")
        self.assertTrue(chatbot)
        self.assertEqual(chatbot.timeout, smarter_settings.smarter_default_http_timeout)
        self.assertEqual(chatbot.name, "netec-demo")
        self.assertIsInstance(chatbot.chatbot_description, str)
        self.assertIsInstance(chatbot.chatbot_version, str)
        self.assertIsInstance(chatbot.status, dict)
        self.assertIsInstance(chatbot.chatbot_id, int)
        self.assertIsInstance(chatbot.chatbot_metadata, dict)
        self.assertIsInstance(chatbot.spec, dict)
        self.assertIsInstance(chatbot.status, dict)
        self.assertIsInstance(chatbot.config, dict)

        self.assertEqual(chatbot.config["provider"], "openai")
        self.assertEqual(chatbot.config["defaultModel"], "gpt-4o")
        self.assertEqual(chatbot.config["defaultMaxTokens"], 4096)
        self.assertEqual(chatbot.config["defaultTemperature"], 1.0)

        self.assertEqual(chatbot.chatbot_metadata["name"], "netec-demo")
        self.assertIsInstance(chatbot.status["deployed"], bool)

        # "sandboxUrl": "https://platform.smarter.sh/api/v1/chatbots/36/",
        self.assertEqual(chatbot.sandbox_url.scheme, "https")
        self.assertEqual(chatbot.sandbox_url.netloc, "platform.smarter.sh")
        self.assertRegex(chatbot.sandbox_url.path, r"/api/v1/chatbots/\d+/")

        # "urlChatapp": "https://netec-demo.3141-5926-5359.api.smarter.sh/chatapp/"
        self.assertEqual(chatbot.url_chatapp.scheme, "https")
        self.assertEqual(chatbot.url_chatapp.netloc, "netec-demo.3141-5926-5359.api.smarter.sh")
        self.assertEqual(chatbot.url_chatapp.path, "/chatapp/")

        # "urlChatbot": "https://platform.smarter.sh/api/v1/chatbots/36/chat/"
        self.assertEqual(chatbot.url_chatbot.scheme, "https")
        self.assertEqual(chatbot.url_chatbot.netloc, "platform.smarter.sh")
        self.assertRegex(chatbot.url_chatbot.path, r"/api/v1/chatbots/\d+/chat/")
        self.assertEqual(chatbot.url_chatbot.path, f"/api/v1/chatbots/{chatbot.chatbot_id}/chat/")

    def test_chatbot_prompt(self):
        chatbot = Chatbot(name="netec-demo", timeout=61)
        chat = chatbot.prompt("Hello, World!")
        print("test_chatbot_prompt() prompt response: ", chat)
        self.assertIsInstance(chat, str)
        self.assertEqual(chatbot.timeout, 61)

    def test_chatbot_default_addressing(self):
        client = Smarter(timeout=61)
        chatbot = client.resources.chatbots.get(name="netec-demo")
        self.assertEqual(chatbot.timeout, 61)
        self.assertEqual(chatbot.name, "netec-demo")

    def test_plugin(self):
        plugin = Plugin()
        self.assertTrue(plugin)

    def test_account(self):
        account = Account()
        self.assertTrue(account)

    def test_client_resource(self):
        client = Smarter(api_key=smarter_settings.smarter_api_key.get_secret_value())
        self.assertTrue(client)
        chatbot = client.resources.chatbots.get(name="netec-demo")
        self.assertTrue(chatbot)
        self.assertEqual(chatbot.name, "netec-demo")
        chat = chatbot.prompt("Hello, World from client.resources.chatbots.get(name='netec-demo')")
        print("test_client_resource() prompt response: ", chat)
        self.assertIsInstance(chat, str)


if __name__ == "__main__":
    unittest.main()
