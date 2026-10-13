"""Test smarter.resources.providers."""

from .base import SmarterTestBase


class TestProviders(SmarterTestBase):
    """Test Providers."""

    def test_providers(self):
        """Providers are listed and retrieved, with their models."""
        self.route("GET", "providers/", json_body=[{"name": "openai", "baseUrl": "https://api.openai.com/v1/"}])
        self.route("GET", "providers/openai/", json_body={"name": "openai", "isActive": True})
        self.route("GET", "providers/openai/models/", json_body=[{"name": "gpt-4o-mini", "supportsTools": True}])
        self.assertEqual(self.client.providers.list()[0].base_url, "https://api.openai.com/v1/")
        self.assertTrue(self.client.providers.retrieve("openai").is_active)
        self.assertTrue(self.client.providers.models("openai")[0].supports_tools)
