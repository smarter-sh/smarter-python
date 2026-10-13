"""Test smarter.core.conf."""

import os
import tempfile
from pathlib import Path

from smarter.core.conf import (
    CliConfig,
    SmarterSettings,
    api_base_url,
    environment_url,
    resolve_client_config,
)
from smarter.core.exceptions import SmarterConfigurationError

from .base import SmarterTestBase

CLI_CONFIG = """
config:
  account_number: 1234-5678-9012
  environment: alpha
  root_domain: example.com
local:
  api_key: local-key
alpha:
  api_key: alpha-key
prod:
  api_key: ""
"""


class TestConf(SmarterTestBase):
    """Test the resolution of a client's configuration."""

    def write_cli_config(self, text: str) -> Path:
        """A cli configuration file with the given text."""
        directory = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "config.yaml"
        path.write_text(text, encoding="utf-8")
        return path

    def settings(self, **kwargs) -> SmarterSettings:
        """Settings without a cli configuration file, unless one is given."""
        kwargs.setdefault("config_file", Path("/no/such/config.yaml"))
        return SmarterSettings(**kwargs)

    def test_environment_url(self):
        """Each environment's url is derived as the cli derives it."""
        self.assertEqual(environment_url("local", "example.com"), "http://localhost:9357")
        self.assertEqual(environment_url("prod", "example.com"), "https://example.com")
        self.assertEqual(environment_url("beta", "example.com"), "https://beta.example.com")

    def test_api_base_url(self):
        """A platform url gets the api's path and a trailing slash, once."""
        for url in (
            "https://example.com",
            "https://example.com/",
            "https://example.com/api/v1",
            " https://example.com/api/v1/ ",
        ):
            with self.subTest(url=url):
                self.assertEqual(api_base_url(url), "https://example.com/api/v1/")
        self.assertEqual(api_base_url("http://host:9357/prefix"), "http://host:9357/prefix/api/v1/")

    def test_api_base_url_rejects_non_http(self):
        """A url that is not http or https is a configuration error."""
        for url in ("ftp://example.com", "example.com", ""):
            with self.subTest(url=url), self.assertRaises(SmarterConfigurationError):
                api_base_url(url)

    def test_arguments_win(self):
        """Explicit arguments win over settings."""
        config = resolve_client_config(
            api_key="arg-key",
            base_url="https://arg.example.com",
            environment="beta",
            timeout=5,
            max_retries=7,
            settings=self.settings(api_key="env-key", base_url="https://env.example.com", timeout=9, max_retries=1),
        )
        self.assertEqual(config.api_key.get_secret_value(), "arg-key")
        self.assertEqual(config.base_url, "https://arg.example.com/api/v1/")
        self.assertEqual(config.environment, "beta")
        self.assertEqual(config.timeout, 5)
        self.assertEqual(config.max_retries, 7)

    def test_settings(self):
        """The SMARTER_* settings are used when there are no arguments."""
        config = resolve_client_config(
            settings=self.settings(api_key="env-key", environment="next", root_domain="x.io")
        )
        self.assertEqual(config.api_key.get_secret_value(), "env-key")
        self.assertEqual(config.base_url, "https://next.x.io/api/v1/")

    def test_defaults(self):
        """Without configuration, the client uses prod on platform.smarter.sh."""
        config = resolve_client_config(api_key="k", settings=self.settings())
        self.assertEqual(config.environment, "prod")
        self.assertEqual(config.base_url, "https://platform.smarter.sh/api/v1/")

    def test_cli_config_file(self):
        """The cli's configuration file supplies the environment, the root domain, and the environment's api key."""
        path = self.write_cli_config(CLI_CONFIG)
        config = resolve_client_config(settings=self.settings(config_file=path))
        self.assertEqual(config.environment, "alpha")
        self.assertEqual(config.api_key.get_secret_value(), "alpha-key")
        self.assertEqual(config.base_url, "https://alpha.example.com/api/v1/")
        local = resolve_client_config(environment="local", settings=self.settings(config_file=path))
        self.assertEqual(local.api_key.get_secret_value(), "local-key")
        self.assertEqual(local.base_url, "http://localhost:9357/api/v1/")

    def test_cli_config_top_level_key(self):
        """The cli's top-level api_key is used by an environment without its own key."""
        path = self.write_cli_config(CLI_CONFIG + "api_key: top-key\n")
        config = resolve_client_config(environment="prod", settings=self.settings(config_file=path))
        self.assertEqual(config.api_key.get_secret_value(), "top-key")

    def test_no_api_key(self):
        """A missing api key is a configuration error that says how to set one."""
        with self.assertRaises(SmarterConfigurationError) as context:
            resolve_client_config(settings=self.settings())
        self.assertIn("SMARTER_API_KEY", str(context.exception))

    def test_cli_config_unreadable(self):
        """A missing, malformed or invalid cli configuration file is ignored."""
        self.assertEqual(CliConfig.load(Path("/no/such/file.yaml")), CliConfig())
        self.assertEqual(CliConfig.load(self.write_cli_config("{not: [valid")), CliConfig())
        self.assertEqual(CliConfig.load(self.write_cli_config("- a list\n")), CliConfig())
        with self.assertLogs("smarter.core.conf", level="WARNING"):
            self.assertEqual(CliConfig.load(self.write_cli_config("config:\n  environment: mars\n")), CliConfig())

    def test_settings_from_environment(self):
        """SmarterSettings reads the SMARTER_* environment variables."""
        with self.subTest("defaults"):
            settings = SmarterSettings()
            self.assertIsNone(settings.api_key)
            self.assertEqual(settings.max_retries, 2)
        os.environ["SMARTER_API_KEY"] = "from-env"
        os.environ["SMARTER_TIMEOUT"] = "12.5"
        settings = SmarterSettings()
        self.assertEqual(settings.api_key.get_secret_value(), "from-env")  # type: ignore[union-attr]
        self.assertEqual(settings.timeout, 12.5)
