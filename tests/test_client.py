"""Test smarter.client."""

from smarter import Smarter, __version__
from smarter.models.manifest import KindInfo
from smarter.models.platform import PlatformStatus, PlatformVersion, WhoAmI
from smarter.resources import (
    Accounts,
    Guardrails,
    Journal,
    LLMClients,
    LLMHosts,
    Manifests,
    MCPClients,
    Orchestrators,
    Plugins,
    PromptHistory,
    Providers,
    Proxies,
    Secrets,
    Vectorsearches,
    Vectorstores,
)

from .base import API, API_KEY, SmarterTestBase


class TestClient(SmarterTestBase):
    """Test the Smarter client."""

    def test_platform(self):
        """The platform endpoints return the data of their journaled responses."""
        for path in ("whoami", "version", "status", "resources"):
            self.route("POST", f"cli/{path}/", fixture=path)
        whoami = self.client.whoami()
        self.assertIsInstance(whoami, WhoAmI)
        self.assertEqual(whoami.account.account_number, "1234-5678-9012")
        self.assertIsInstance(self.client.version(), PlatformVersion)
        self.assertIsInstance(self.client.status(), PlatformStatus)
        kinds = self.client.kinds()
        self.assertTrue(all(isinstance(kind, KindInfo) for kind in kinds))

    def test_resources(self):
        """Each attribute is its resource, created once."""
        expected = {
            "manifests": Manifests,
            "llm_clients": LLMClients,
            "guardrails": Guardrails,
            "mcp_clients": MCPClients,
            "vectorstores": Vectorstores,
            "llm_hosts": LLMHosts,
            "secrets": Secrets,
            "plugins": Plugins,
            "orchestrators": Orchestrators,
            "vectorsearches": Vectorsearches,
            "accounts": Accounts,
            "history": PromptHistory,
            "journal": Journal,
            "providers": Providers,
            "proxies": Proxies,
        }
        for name, resource_class in expected.items():
            with self.subTest(name=name):
                self.assertIsInstance(getattr(self.client, name), resource_class)
                self.assertIs(getattr(self.client, name), getattr(self.client, name))

    def test_properties(self):
        """The api key and base url, and a repr that masks the key."""
        self.assertEqual(self.client.api_key, API_KEY)
        self.assertEqual(self.client.base_url, API)
        self.assertNotIn(API_KEY, repr(self.client))
        self.assertIn("****beef", repr(self.client))
        self.assertTrue(__version__)

    def test_context_manager(self):
        """The client closes its connections on exit."""
        with Smarter(api_key=API_KEY, base_url="http://testserver") as client:
            http_client = client.http._http_client  # pylint: disable=protected-access
        self.assertTrue(http_client.is_closed)
