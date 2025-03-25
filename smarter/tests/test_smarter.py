"""
top-level test file for the smarter package.
"""

import unittest

from smarter.api import Client
from smarter.common.conf import settings as smarter_settings
from smarter.common.const import SmarterEnvironments
from smarter.resources import Account, Chatbot, Plugin


class TestSample(unittest.TestCase):
    """
    to verify that our codebase if free of syntax errors.
    """

    def test_example(self):
        self.assertEqual(1 + 1, 2)

    def test_settings(self):
        self.assertTrue(smarter_settings)
        self.assertEqual(smarter_settings.root_domain, "smarter.sh")
        self.assertEqual(smarter_settings.environment, SmarterEnvironments.PROD)

    def test_client(self):
        client = Client()
        self.assertTrue(client)

    def test_chatbot(self):
        chatbot = Chatbot(name="netec-demo")
        self.assertTrue(chatbot)

    def test_plugin(self):
        plugin = Plugin()
        self.assertTrue(plugin)

    def test_account(self):
        account = Account()
        self.assertTrue(account)


if __name__ == "__main__":
    unittest.main()
