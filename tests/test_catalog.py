"""Test smarter.resources.catalog."""

from smarter.core.exceptions import SmarterValueError

from .base import SmarterTestBase


class TestCatalog(SmarterTestBase):
    """Test Secrets, Plugins, Orchestrators and Vectorsearches."""

    def test_secrets(self):
        """Secrets are listed and retrieved, without their values."""
        self.route("GET", "secrets/", fixture="secrets")
        self.route("GET", "secrets/1/", json_body=self.load_json("secrets")[0])
        self.assertEqual(self.client.secrets.list()[0].name, "anthropic_api_key")
        self.assertIsNotNone(self.client.secrets.retrieve(1).last_accessed)

    def test_plugins(self):
        """Plugins are listed, and described and deleted by their own kind."""
        plugins = self.load_json("plugins")
        plugins[0]["kind"] = "SqlPlugin"
        self.route("GET", "plugins/", json_body=plugins)
        manifest = {
            "apiVersion": "smarter.sh/v1",
            "kind": "SqlPlugin",
            "metadata": {"name": plugins[0]["name"]},
            "spec": {},
        }
        self.route("GET", "plugins/355/", json_body=manifest)
        self.route(
            "POST",
            "cli/describe/SqlPlugin/",
            json_body={"data": {"kind": "SqlPlugin", "metadata": {"name": plugins[0]["name"]}}},
        )
        self.route("POST", "cli/delete/SqlPlugin/", json_body={"message": "deleted"})
        name = plugins[0]["name"]
        self.assertEqual(self.client.plugins.kind_of(name), "SqlPlugin")
        self.assertEqual(self.client.plugins.describe(name).kind, "SqlPlugin")
        self.assertEqual(self.client.plugins.delete(name).message, "deleted")
        retrieved = self.client.plugins.retrieve(355)
        self.assertEqual((retrieved.kind, retrieved.metadata.name), ("SqlPlugin", name))

    def test_plugin_apply(self):
        """Apply() accepts any plugin kind, and refuses other kinds."""
        self.route("POST", "cli/apply/", json_body={"message": "applied"})
        manifest = {"kind": "ApiPlugin", "metadata": {"name": "p"}, "spec": {}}
        self.assertEqual(self.client.plugins.apply(manifest).message, "applied")
        with self.assertRaises(SmarterValueError):
            self.client.plugins.apply({**manifest, "kind": "Secret"})

    def test_orchestrators_and_vectorsearches(self):
        """Orchestrators and vectorsearches are listed."""
        self.route("GET", "orchestrators/", json_body=[])
        self.route("GET", "vectorsearches/", json_body=[{"id": 1, "name": "v"}])
        self.assertEqual(self.client.orchestrators.list(), [])
        self.assertEqual(self.client.vectorsearches.list()[0].name, "v")
