"""Test smarter.resources.proxies."""

from .base import API, SmarterTestBase


class TestProxies(SmarterTestBase):
    """Test Proxies."""

    def test_list_and_base_url(self):
        """Proxies are listed, and a proxy's base url is for a provider's own SDK."""
        self.route("GET", "proxy/", fixture="proxy")
        proxy = self.client.proxies.list()[0]
        self.assertTrue(proxy.allowed_paths)
        self.assertEqual(self.client.proxies.base_url("openai"), f"{API}proxy/openai/")

    def test_request(self):
        """Request() sends the provider's request through the proxy."""
        self.route("POST", "proxy/openai/v1/chat/completions", json_body={"id": "chatcmpl-1"})
        response = self.client.proxies.request("openai", "/v1/chat/completions", json={"model": "m"})
        self.assertEqual(response, {"id": "chatcmpl-1"})
        self.assertEqual(self.request_json(), {"model": "m"})
        self.route("GET", "proxy/openai/v1/models", json_body={"data": []})
        self.assertEqual(
            self.client.proxies.request("openai", "v1/models", method="get", params={"limit": 1}), {"data": []}
        )
