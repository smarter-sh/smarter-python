"""
The configuration of the Smarter SDK.

A client needs an api key and the base url of a Smarter platform. Each is taken from the first of
these that sets it:

1. the arguments of :class:`smarter.Smarter`,
2. environment variables: ``SMARTER_API_KEY``, ``SMARTER_BASE_URL``, ``SMARTER_ENVIRONMENT``,
   ``SMARTER_ROOT_DOMAIN``, ``SMARTER_TIMEOUT``, ``SMARTER_MAX_RETRIES`` and ``SMARTER_LOG``
   (:class:`SmarterSettings`),
3. the ``smarter`` cli's configuration file, ``~/.smarter/config.yaml`` (``SMARTER_CONFIG_FILE``),
   so that a developer who has run ``smarter configure`` needs no other setup,
4. the defaults: the ``prod`` environment of ``platform.smarter.sh``.

Without an explicit base url, the url is derived from the environment as the cli derives it:
``local`` is ``http://localhost:9357``, ``alpha``, ``beta`` and ``next`` are
``https://<environment>.<root domain>``, and ``prod`` is ``https://<root domain>``.

This follows the Smarter platform's settings design (ADR-007): one validated Pydantic settings
model is the only place that reads the environment.
"""

import logging
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit, urlunsplit

import yaml
from pydantic import BaseModel, Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import SmarterConfigurationError

logger = logging.getLogger(__name__)

SmarterEnvironment = Literal["local", "alpha", "beta", "next", "prod"]
"""The environments of the smarter cli's configuration file."""

DEFAULT_ENVIRONMENT: SmarterEnvironment = "prod"
DEFAULT_ROOT_DOMAIN = "platform.smarter.sh"
LOCAL_URL = "http://localhost:9357"
"""The url of the Smarter platform's local development server."""

API_PATH = "/api/v1/"
"""The path of the Smarter api, which every request url is relative to."""

DEFAULT_TIMEOUT = 60.0
"""Seconds.

Prompts that call several tools can take tens of seconds.
"""

DEFAULT_MAX_RETRIES = 2
DEFAULT_CONFIG_FILE = Path.home() / ".smarter" / "config.yaml"


class SmarterSettings(BaseSettings):
    """The SDK's settings, from ``SMARTER_*`` environment variables."""

    model_config = SettingsConfigDict(env_prefix="SMARTER_", extra="ignore")

    api_key: SecretStr | None = Field(None, description="A Smarter api key: 64 characters.")
    base_url: str | None = Field(None, description="e.g. https://platform.example.com or http://localhost:9357.")
    environment: SmarterEnvironment | None = None
    root_domain: str | None = Field(None, description="The platform's root domain, e.g. platform.smarter.sh.")
    timeout: float = Field(DEFAULT_TIMEOUT, gt=0)
    max_retries: int = Field(DEFAULT_MAX_RETRIES, ge=0)
    config_file: Path = DEFAULT_CONFIG_FILE
    log: Literal["debug", "info"] | None = Field(None, description="Log the SDK's requests to stderr.")


class CliConfig(BaseModel):
    """The parts of the smarter cli's ``~/.smarter/config.yaml`` that the SDK reads."""

    environment: SmarterEnvironment | None = None
    root_domain: str | None = None
    api_key: SecretStr | None = Field(None, description="The top-level api_key, used by any environment.")
    api_keys: dict[str, SecretStr] = Field(default_factory=dict, description="The api key of each environment.")

    @classmethod
    def load(cls, path: Path) -> "CliConfig":
        """
        Read the cli's configuration file.

        A missing or unreadable file is an empty configuration: the file is optional.

        :param path: The file's path.
        :returns: The configuration.
        """
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as e:
            logger.debug("smarter cli configuration %s not read: %s", path, e)
            return cls()
        if not isinstance(document, dict):
            return cls()
        config = document.get("config") if isinstance(document.get("config"), dict) else {}
        api_keys = {
            name: section["api_key"]
            for name, section in document.items()
            if isinstance(section, dict) and isinstance(section.get("api_key"), str) and section["api_key"]
        }
        top_level_key = document.get("api_key")
        try:
            return cls(
                environment=config.get("environment") or None,
                root_domain=config.get("root_domain") or None,
                api_key=top_level_key if isinstance(top_level_key, str) and top_level_key else None,
                api_keys=api_keys,
            )
        except ValidationError as e:
            logger.warning("smarter cli configuration %s is invalid and was ignored: %s", path, e)
            return cls()


class ClientConfig(BaseModel):
    """A client's resolved configuration."""

    api_key: SecretStr
    base_url: str = Field(..., description="The api's base url, ending in /api/v1/.")
    environment: SmarterEnvironment
    timeout: float
    max_retries: int


def environment_url(environment: SmarterEnvironment, root_domain: str) -> str:
    """
    The platform url of an environment, as the smarter cli derives it.

    :param environment: The environment.
    :param root_domain: The platform's root domain, e.g. ``platform.smarter.sh``.
    :returns: e.g. ``https://alpha.platform.smarter.sh``.
    """
    if environment == "local":
        return LOCAL_URL
    if environment == "prod":
        return f"https://{root_domain}"
    return f"https://{environment}.{root_domain}"


def api_base_url(url: str) -> str:
    """
    The api's base url for a platform url.

    ``https://example.com`` and ``https://example.com/api/v1`` both become
    ``https://example.com/api/v1/``.

    :param url: A platform url, with or without the api's path.
    :returns: The url, with the api's path and a trailing slash.
    :raises SmarterConfigurationError: If the url is not an http or https url.
    """
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise SmarterConfigurationError(f"The Smarter base url must be an http or https url, not {url!r}.")
    path = parts.path.rstrip("/")
    if not path.endswith(API_PATH.rstrip("/")):
        path = path + API_PATH.rstrip("/")
    return urlunsplit((parts.scheme, parts.netloc, path + "/", "", ""))


def resolve_client_config(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    environment: SmarterEnvironment | None = None,
    timeout: float | None = None,
    max_retries: int | None = None,
    settings: SmarterSettings | None = None,
) -> ClientConfig:
    """
    Resolve a client's configuration from its arguments, the environment, and the cli's configuration file.

    :param api_key: The api key, or None to look it up.
    :param base_url: The platform's url, or None to derive it from the environment.
    :param environment: The environment, or None to look it up.
    :param timeout: The request timeout in seconds, or None for the setting.
    :param max_retries: How many times to retry a failed request, or None for the setting.
    :param settings: The settings to use instead of reading the environment variables, for tests.
    :returns: The configuration.
    :raises SmarterConfigurationError: If no api key is found, or the base url is invalid.
    """
    settings = settings or SmarterSettings()
    cli = CliConfig.load(settings.config_file)
    resolved_environment: SmarterEnvironment = (
        environment or settings.environment or cli.environment or DEFAULT_ENVIRONMENT
    )

    key: str | None = api_key
    if not key and settings.api_key:
        key = settings.api_key.get_secret_value()
    if not key and resolved_environment in cli.api_keys:
        key = cli.api_keys[resolved_environment].get_secret_value()
    if not key and cli.api_key:
        key = cli.api_key.get_secret_value()
    if not key:
        raise SmarterConfigurationError(
            "No Smarter api key. Pass api_key=..., set SMARTER_API_KEY, or run 'smarter configure'."
        )

    url = base_url or settings.base_url
    if not url:
        root_domain = settings.root_domain or cli.root_domain or DEFAULT_ROOT_DOMAIN
        url = environment_url(resolved_environment, root_domain)

    return ClientConfig(
        api_key=SecretStr(key),
        base_url=api_base_url(url),
        environment=resolved_environment,
        timeout=timeout if timeout is not None else settings.timeout,
        max_retries=max_retries if max_retries is not None else settings.max_retries,
    )


__all__ = [
    "API_PATH",
    "CliConfig",
    "ClientConfig",
    "DEFAULT_CONFIG_FILE",
    "DEFAULT_ENVIRONMENT",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_ROOT_DOMAIN",
    "DEFAULT_TIMEOUT",
    "LOCAL_URL",
    "SmarterEnvironment",
    "SmarterSettings",
    "api_base_url",
    "environment_url",
    "resolve_client_config",
]
