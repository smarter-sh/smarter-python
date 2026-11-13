"""Test smarter.resources.extensions."""

import io
import tempfile
from pathlib import Path

from smarter.core.exceptions import BadRequestError, NotFoundError, PermissionDeniedError

from .base import SmarterTestBase


class TestExtensions(SmarterTestBase):
    """Test Extensions."""

    def test_list(self):
        """The installed extensions are listed, with the state of the registry."""
        self.route("GET", "extensions/", fixture="extensions")
        extensions = self.client.extensions.list()
        self.assertTrue(extensions.registry_enabled)
        self.assertEqual(extensions.updates_available, 0)
        self.assertEqual(
            [extension.slug for extension in extensions.objects], ["calculator", "date-calculator", "weather"]
        )
        self.assertEqual(extensions.objects[0].trust_badge, "official")
        self.assertIsNotNone(extensions.objects[0].latest_checked_at)

    def test_registry(self):
        """The registry is read from the cache, or refreshed."""
        self.route("GET", "extensions/registry/", fixture="extension_registry")
        registry = self.client.extensions.registry()
        self.assertEqual(dict(self.last_request.url.params), {})
        self.assertTrue(registry.enabled)
        self.assertIsNone(registry.error)
        entry = registry.objects[0]
        self.assertEqual((entry.slug, entry.action), ("calculator", "installed"))
        self.assertTrue(entry.versions[0].compatible)
        self.client.extensions.registry(refresh=True)
        self.assertEqual(dict(self.last_request.url.params), {"refresh": "true"})

    def test_retrieve(self):
        """An extension is retrieved with its tools, settings and versions."""
        self.route("GET", "extensions/weather/", fixture="extension")
        extension = self.client.extensions.retrieve("weather")
        self.assertEqual(extension.display_name, "Weather")
        self.assertEqual(extension.tools[0].function_name, "ext_weather_get_weather")
        self.assertEqual(extension.settings[0].type, "secret")
        self.assertTrue(extension.settings[0].is_set)
        self.assertEqual(extension.settings[1].default, "https://api.open-meteo.com/v1/forecast")
        self.assertTrue(extension.versions[0].is_installed)
        self.assertTrue(extension.all_accounts)
        self.assertEqual(extension.available_secrets[0].name, "google_maps_api_key")

    def test_retrieve_missing(self):
        """An extension that is not installed raises NotFoundError with the platform's message."""
        self.route("GET", "extensions/nope/", status=404, json_body={"detail": "No extension nope is installed."})
        with self.assertRaises(NotFoundError) as context:
            self.client.extensions.retrieve("nope")
        self.assertEqual(context.exception.message, "No extension nope is installed.")

    def test_check_updates(self):
        """Check_updates() returns the platform's message, without an extension."""
        self.route(
            "POST",
            "extensions/check-updates/",
            json_body={"message": "Every extension is up to date.", "extension": None},
        )
        result = self.client.extensions.check_updates()
        self.assertEqual(result.message, "Every extension is up to date.")
        self.assertIsNone(result.extension)

    def test_forbidden(self):
        """An action of a user who is not a superuser raises PermissionDeniedError."""
        self.route(
            "POST",
            "extensions/check-updates/",
            status=403,
            json_body={"detail": "Only superusers may manage extensions."},
        )
        with self.assertRaises(PermissionDeniedError):
            self.client.extensions.check_updates()

    def test_install(self):
        """Install() sends the slug, and the version only when it is given."""
        self.route("POST", "extensions/install/", fixture="extension_action")
        result = self.client.extensions.install("calculator")
        self.assertEqual(result.extension.slug, "calculator")  # type: ignore[union-attr]
        self.assertEqual(self.request_json(), {"slug": "calculator"})
        self.client.extensions.install("calculator", version="0.1.0")
        self.assertEqual(self.request_json(), {"slug": "calculator", "version": "0.1.0"})

    def test_install_rejected(self):
        """The platform's validation error is raised with its message."""
        self.route(
            "POST",
            "extensions/install/",
            status=400,
            json_body={"detail": "The request is not valid: slug: Field required"},
        )
        with self.assertRaises(BadRequestError) as context:
            self.client.extensions.install("")
        self.assertIn("slug", context.exception.message)

    def test_upload(self):
        """Upload() sends the archive as multipart/form-data, from a path or a file object."""
        self.route("POST", "extensions/upload/", fixture="extension_action")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "weather-0.2.1.zip"
            path.write_bytes(b"PK\x03\x04")
            self.client.extensions.upload(path)
            self.assertIn(b'name="archive"; filename="weather-0.2.1.zip"', self.last_request.content)
            self.assertIn(b"Content-Type: application/zip", self.last_request.content)
            self.client.extensions.upload(str(path))
            self.assertIn(b'filename="weather-0.2.1.zip"', self.last_request.content)
            with open(path, "rb") as handle:
                self.client.extensions.upload(handle)
            self.assertIn(b'filename="weather-0.2.1.zip"', self.last_request.content)
        self.client.extensions.upload(io.BytesIO(b"PK\x03\x04"))
        self.assertIn(b'filename="extension.zip"', self.last_request.content)

    def test_lifecycle_actions(self):
        """Enable, disable, update and uninstall post no body to the extension's action."""
        for action in ("enable", "disable", "update", "uninstall"):
            with self.subTest(action=action):
                self.route("POST", f"extensions/weather/{action}/", fixture="extension_action")
                result = getattr(self.client.extensions, action)("weather")
                self.assertEqual(result.message, "Calculator is available to every account.")
                self.assertEqual(self.last_request.content, b"")

    def test_rollback(self):
        """Rollback() sends the version's id."""
        self.route("POST", "extensions/weather/rollback/", fixture="extension_action")
        self.client.extensions.rollback("weather", 3)
        self.assertEqual(self.request_json(), {"versionId": 3})

    def test_configure(self):
        """Configure() sends values, and secrets as a new value, an existing Secret, or nothing to clear one."""
        self.route("POST", "extensions/weather/configure/", fixture="extension_action")
        self.client.extensions.configure(
            "weather",
            values={"weather_api_url": None, "verbose": True},
            secrets={"a": "value", "b": 6, "c": None},
        )
        self.assertEqual(
            self.request_json(),
            {
                "values": {"weather_api_url": None, "verbose": True},
                "secrets": {"a": {"value": "value"}, "b": {"secretId": 6}, "c": {}},
            },
        )
        self.client.extensions.configure("weather")
        self.assertEqual(self.request_json(), {"values": {}, "secrets": {}})

    def test_set_availability(self):
        """Set_availability() sends every account, or the accounts' ids."""
        self.route("POST", "extensions/calculator/availability/", fixture="extension_action")
        result = self.client.extensions.set_availability("calculator", True)
        self.assertTrue(result.extension.all_accounts)  # type: ignore[union-attr]
        self.assertEqual(self.request_json(), {"allAccounts": True, "accountIds": []})
        self.client.extensions.set_availability("calculator", False, account_ids=(1, 2))
        self.assertEqual(self.request_json(), {"allAccounts": False, "accountIds": [1, 2]})
