"""
top-level test file for the smarter package.
"""

import unittest

from smarter.api import Client
from smarter.common.conf import settings as smarter_settings
from smarter.common.const import SmarterEnvironments
from smarter.common.mixins import DEFAULT_API_ENDPOINT
from smarter.resources import Account, Chatbot, Plugin


class TestApi(unittest.TestCase):
    """
    to verify that our codebase if free of syntax errors.
    """

    def test_settings(self):
        self.assertTrue(smarter_settings)
        self.assertEqual(smarter_settings.root_domain, "smarter.sh")
        self.assertEqual(smarter_settings.environment, SmarterEnvironments.PROD)

    def test_client(self):
        client = Client()
        self.assertTrue(client)
        self.assertEqual(client.base_url, "https://platform.smarter.sh/api/v1/")
        self.assertEqual(client.url_endpoint, DEFAULT_API_ENDPOINT)
        self.assertEqual(client.url, "https://platform.smarter.sh/api/v1/cli/whoami/")
        self.assertEqual(client.api_key, smarter_settings.smarter_api_key)
        self.assertEqual(client.api, "smarter.sh/v1")
        self.assertEqual(client.thing, "None")
        self.assertIn("key", client.metadata)

    def test_chatbot(self):
        chatbot = Chatbot(name="netec-demo")
        self.assertTrue(chatbot)
        self.assertEqual(chatbot.name, "netec-demo")
        self.assertIsInstance(chatbot.description, str)
        self.assertIsInstance(chatbot.version, str)
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
        chatbot = Chatbot(name="netec-demo")
        chat = chatbot.prompt("Hello, World!")
        print("prompt response: ", chat)
        self.assertIsInstance(chat, str)

    def test_plugin(self):
        plugin = Plugin()
        self.assertTrue(plugin)

    def test_account(self):
        account = Account()
        self.assertTrue(account)


if __name__ == "__main__":
    unittest.main()
