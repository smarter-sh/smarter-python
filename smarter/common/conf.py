# pylint: disable=no-member,no-self-argument,unused-argument,R0801,too-many-lines
"""
Smarter Python Library Configuration.

This module overrides Python environment-based settings modules and provides
strongly typed and validated alternative settings values. It uses the pydantic_settings
library to validate the configuration values. The configuration values are initialized
according to the following prioritization sequence:
    1. Python __init__.py module
    2. environment variables (os.environ)
    3. Python settings module
    4. SettingsDefaults

The Settings class also provides a dump property that returns a dictionary of all
configuration values. This is useful for debugging and logging.
"""

import importlib

# python stuff
import logging
import os  # library for interacting with the operating system
import platform  # library to view information about the server host this module runs on
import re
from functools import cached_property
from typing import Any, List, Optional
from urllib.parse import urljoin

# 3rd party stuff
import pkg_resources
from dotenv import load_dotenv
from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings

# our stuff
from .const import (
    SMARTER_API_VERSION,
    SMARTER_DEFAULT_CACHE_TIMEOUT,
    SMARTER_DEFAULT_HTTP_TIMEOUT,
    SMARTER_MAX_CACHE_SIZE,
    SMARTER_PLATFORM_SUBDOMAIN,
    VERSION,
    SmarterEnvironments,
)
from .exceptions import SmarterConfigurationError
from .utils import recursive_sort_dict
from .validators import SmarterValidator


logger = logging.getLogger(__name__)
DOT_ENV_LOADED = load_dotenv()


def get_semantic_version() -> str:
    """
    Return the semantic version number.

    Example valid values of __version__.py are:
    0.1.17
    0.1.17-alpha.1
    0.1.17-beta.1
    0.1.17-next.1
    0.1.17-next.2
    0.1.17-next.123456
    0.1.17-next-major.1
    0.1.17-next-major.2
    0.1.17-next-major.123456

    Note:
    - pypi does not allow semantic version numbers to contain a dash.
    - pypi does not allow semantic version numbers to contain a 'v' prefix.
    - pypi does not allow semantic version numbers to contain a 'next' suffix.
    """
    if not isinstance(VERSION, dict):
        return "unknown"

    version = VERSION.get("__version__")
    if not version:
        return "unknown"
    version = re.sub(r"-next\.\d+", "", version)
    return re.sub(r"-next-major\.\d+", "", version)


# pylint: disable=too-few-public-methods
class SettingsDefaults:
    """
    Default values for Settings. This takes care of most of what we're interested in.
    It initializes from the following prioritization sequence:
      1. environment variables
      2. tfvars
      3. defaults.
    """

    LLM_DEFAULT_PROVIDER = "openai"
    LLM_DEFAULT_MODEL = "gpt-4o-mini"
    LLM_DEFAULT_SYSTEM_ROLE = (
        "You are a helpful chatbot. When given the opportunity to utilize "
        "function calling, you should always do so. This will allow you to "
        "provide the best possible responses to the user. If you are unable to "
        "provide a response, you should prompt the user for more information. If "
        "you are still unable to provide a response, you should inform the user "
        "that you are unable to help them at this time."
    )
    LLM_DEFAULT_TEMPERATURE = 0.5
    LLM_DEFAULT_MAX_TOKENS = 2048

    # defaults for this Python package
    ROOT_DOMAIN = os.environ.get("SMARTER_ROOT_DOMAIN", "smarter.sh")
    SHARED_RESOURCE_IDENTIFIER = os.environ.get("SMARTER_SHARED_RESOURCE_IDENTIFIER", "smarter")
    DEBUG_MODE: bool = os.environ.get("SMARTER_DEBUG_MODE", False)
    DUMP_DEFAULTS: bool = os.environ.get("SMARTER_DUMP_DEFAULTS", False)

    OPENAI_ENDPOINT_IMAGE_N = 4
    OPENAI_ENDPOINT_IMAGE_SIZE = "1024x768"

    LOCAL_HOSTS = ["localhost", "127.0.0.1"]
    LOCAL_HOSTS += [host + ":8000" for host in LOCAL_HOSTS]
    LOCAL_HOSTS.append("testserver")

    SMARTER_ENVIRONMENT = os.environ.get("SMARTER_ENVIRONMENT", SmarterEnvironments.PROD)
    SMARTER_API_KEY = os.environ.get("SMARTER_API_KEY", "")
    SMARTER_DEFAULT_HTTP_TIMEOUT = SMARTER_DEFAULT_HTTP_TIMEOUT
    SMARTER_DEFAULT_CACHE_TIMEOUT = SMARTER_DEFAULT_CACHE_TIMEOUT
    SMARTER_MAX_CACHE_SIZE = SMARTER_MAX_CACHE_SIZE

    @classmethod
    def to_dict(cls):
        """Convert SettingsDefaults to dict"""
        return {
            key: "***MASKED***" if key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"] else value
            for key, value in SettingsDefaults.__dict__.items()
            if not key.startswith("__") and not callable(key) and key != "to_dict"
        }


def empty_str_to_bool_default(v: str, default: bool) -> bool:
    """Convert empty string to default boolean value"""
    if v in [None, ""]:
        return default
    return v.lower() in ["true", "1", "t", "y", "yes"]


def empty_str_to_int_default(v: str, default: int) -> int:
    """Convert empty string to default integer value"""
    if v in [None, ""]:
        return default
    try:
        return int(v)
    except ValueError:
        return default


# pylint: disable=too-many-public-methods
# pylint: disable=too-many-instance-attributes
class Settings(BaseSettings):
    """Settings for Lambda functions"""

    # pylint: disable=too-few-public-methods
    class Config:
        """Pydantic configuration"""

        frozen = True

    _dump: dict = None

    # pylint: disable=too-many-branches,too-many-statements
    def __init__(self, **data: Any):  # noqa: C901
        super().__init__(**data)

        if self.debug_mode:
            logger.setLevel(logging.DEBUG)

        # pylint: disable=logging-fstring-interpolation
        logger.debug("Settings initialized")

    shared_resource_identifier: Optional[str] = Field(
        SettingsDefaults.SHARED_RESOURCE_IDENTIFIER, env="SHARED_RESOURCE_IDENTIFIER"
    )
    debug_mode: Optional[bool] = Field(
        SettingsDefaults.DEBUG_MODE,
        env="DEBUG_MODE",
        pre=True,
        getter=lambda v: empty_str_to_bool_default(v, SettingsDefaults.DEBUG_MODE),
    )
    dump_defaults: Optional[bool] = Field(
        SettingsDefaults.DUMP_DEFAULTS,
        env="DUMP_DEFAULTS",
        pre=True,
        getter=lambda v: empty_str_to_bool_default(v, SettingsDefaults.DUMP_DEFAULTS),
    )
    environment: Optional[str] = Field(
        SettingsDefaults.SMARTER_ENVIRONMENT,
        env="SMARTER_ENVIRONMENT",
    )
    local_hosts: Optional[List[str]] = Field(
        SettingsDefaults.LOCAL_HOSTS,
        env="LOCAL_HOSTS",
    )
    root_domain: Optional[str] = Field(
        SettingsDefaults.ROOT_DOMAIN,
        env="ROOT_DOMAIN",
    )
    init_info: Optional[str] = Field(
        None,
        env="INIT_INFO",
    )
    openai_endpoint_image_n: Optional[int] = Field(
        SettingsDefaults.OPENAI_ENDPOINT_IMAGE_N, env="OPENAI_ENDPOINT_IMAGE_N"
    )
    openai_endpoint_image_size: Optional[str] = Field(
        SettingsDefaults.OPENAI_ENDPOINT_IMAGE_SIZE, env="OPENAI_ENDPOINT_IMAGE_SIZE"
    )
    llm_default_provider: Optional[str] = Field(SettingsDefaults.LLM_DEFAULT_PROVIDER, env="LLM_DEFAULT_PROVIDER")
    llm_default_model: Optional[str] = Field(SettingsDefaults.LLM_DEFAULT_MODEL, env="LLM_DEFAULT_MODEL")
    llm_default_system_role: Optional[str] = Field(
        SettingsDefaults.LLM_DEFAULT_SYSTEM_ROLE, env="LLM_DEFAULT_SYSTEM_ROLE"
    )
    llm_default_temperature: Optional[float] = Field(
        SettingsDefaults.LLM_DEFAULT_TEMPERATURE, env="LLM_DEFAULT_TEMPERATURE"
    )
    llm_default_max_tokens: Optional[int] = Field(SettingsDefaults.LLM_DEFAULT_MAX_TOKENS, env="LLM_DEFAULT_MAX_TOKENS")
    smarter_api_key: Optional[SecretStr] = Field(SettingsDefaults.SMARTER_API_KEY, env="SMARTER_API_KEY")
    smarter_default_cache_timeout: Optional[int] = Field(
        SettingsDefaults.SMARTER_DEFAULT_CACHE_TIMEOUT, env="SMARTER_DEFAULT_CACHE_TIMEOUT"
    )
    smarter_max_cache_size: Optional[int] = Field(SettingsDefaults.SMARTER_MAX_CACHE_SIZE, env="SMARTER_MAX_CACHE_SIZE")
    smarter_default_http_timeout: Optional[int] = Field(
        SettingsDefaults.SMARTER_DEFAULT_HTTP_TIMEOUT, env="SMARTER_DEFAULT_HTTP_TIMEOUT"
    )

    @cached_property
    def environment_domain(self) -> str:
        """Return the complete domain name."""
        if self.environment == SmarterEnvironments.PROD:
            return SMARTER_PLATFORM_SUBDOMAIN + "." + self.root_domain
        if self.environment in SmarterEnvironments.aws_environments:
            return self.environment + "." + SMARTER_PLATFORM_SUBDOMAIN + "." + self.root_domain
        if self.environment == SmarterEnvironments.LOCAL:
            raise SmarterConfigurationError("Local environment is not supported")
        # default domain format
        return SMARTER_PLATFORM_SUBDOMAIN + "." + self.root_domain

    @cached_property
    def environment_url(self) -> str:
        return SmarterValidator.urlify(self.environment_domain, environment=self.environment)

    @cached_property
    def platform_name(self) -> str:
        """Return the platform name."""
        return self.root_domain.split(".")[0]

    @cached_property
    def environment_namespace(self) -> str:
        """Return the Kubernetes namespace for the environment."""
        return f"{self.platform_name}-{SMARTER_PLATFORM_SUBDOMAIN}-{settings.environment}"

    @cached_property
    def platform_domain(self) -> str:
        """Return the platform domain name. ie platform.smarter.sh"""
        return f"{SMARTER_PLATFORM_SUBDOMAIN}.{self.root_domain}"

    @cached_property
    def api_domain(self) -> str:
        """
        Return the root API domain name. ie api.smarter.sh
        alpha = https://alpha.platform.smarter.sh/api/v1/
        """
        return self.root_domain

    @cached_property
    def environment_api_domain(self) -> str:
        """Return the customer API domain name. ie api.alpha.platform.smarter.sh"""
        return self.environment_domain

    @cached_property
    def environment_api_url(self) -> str:
        retval = SmarterValidator.urlify(self.environment_api_domain, environment=self.environment)
        retval = urljoin(retval, "api/")
        retval = urljoin(retval, SMARTER_API_VERSION)
        return SmarterValidator.urlify(retval, environment=self.environment)

    @cached_property
    def is_using_dotenv_file(self) -> bool:
        """Is the dotenv file being used?"""
        return DOT_ENV_LOADED

    @cached_property
    def environment_variables(self) -> List[str]:
        """Environment variables"""
        return list(os.environ.keys())

    @cached_property
    def version(self) -> str:
        """OpenAI API version"""
        return get_semantic_version()

    @cached_property
    def dump(self) -> dict:
        """Dump all settings."""

        def get_installed_packages():
            installed_packages = pkg_resources.working_set
            # pylint: disable=not-an-iterable
            package_list = [(d.project_name, d.version) for d in installed_packages]
            return package_list

        if self._dump:
            return self._dump

        packages = get_installed_packages()
        packages_dict = [{"name": name, "version": version} for name, version in packages]

        self._dump = {
            "settings": {
                "shared_resource_identifier": self.shared_resource_identifier,
                "debug_mode": self.debug_mode,
                "dump_defaults": self.dump_defaults,
                "environment": self.environment,
                "local_hosts": self.local_hosts,
                "root_domain": self.root_domain,
                "environment_domain": self.environment_domain,
                "environment_url": self.environment_url,
                "platform_name": self.platform_name,
                "environment_api_domain": self.environment_api_domain,
                "environment_api_url": self.environment_api_url,
                "platform_domain": self.platform_domain,
                "init_info": self.init_info,
                "openai_endpoint_image_n": self.openai_endpoint_image_n,
                "openai_endpoint_image_size": self.openai_endpoint_image_size,
                "llm_default_provider": self.llm_default_provider,
                "llm_default_model": self.llm_default_model,
                "llm_default_system_role": self.llm_default_system_role,
                "llm_default_temperature": self.llm_default_temperature,
                "llm_default_max_tokens": self.llm_default_max_tokens,
                "smarter_api_key": self.smarter_api_key,
            },
            "environment": {
                "is_using_dotenv_file": self.is_using_dotenv_file,
                "os": os.name,
                "system": platform.system(),
                "release": platform.release(),
                "shared_resource_identifier": self.shared_resource_identifier,
                "debug_mode": self.debug_mode,
                "dump_defaults": self.dump_defaults,
                "version": self.version,
                "python_version": platform.python_version(),
                "python_implementation": platform.python_implementation(),
                "python_compiler": platform.python_compiler(),
                "python_build": platform.python_build(),
                "python_installed_packages": packages_dict,
            },
        }
        if self.dump_defaults:
            settings_defaults = SettingsDefaults.to_dict()
            self._dump["settings_defaults"] = settings_defaults

        if self.is_using_dotenv_file:
            self._dump["environment"]["dotenv"] = self.environment_variables

        self._dump = recursive_sort_dict(self._dump)
        return self._dump

    @field_validator("shared_resource_identifier")
    def validate_shared_resource_identifier(cls, v) -> str:
        """Validate shared_resource_identifier"""
        if v in [None, ""]:
            return SettingsDefaults.SHARED_RESOURCE_IDENTIFIER
        return v

    @field_validator("environment")
    def validate_environment(cls, v) -> str:
        """Validate environment"""
        if v in [None, ""]:
            return SettingsDefaults.SMARTER_ENVIRONMENT
        return v

    @field_validator("local_hosts")
    def validate_local_hosts(cls, v) -> List[str]:
        """Validate local_hosts"""
        if v in [None, ""]:
            return SettingsDefaults.LOCAL_HOSTS
        return v

    @field_validator("debug_mode")
    def parse_debug_mode(cls, v) -> bool:
        """Parse debug_mode"""
        if isinstance(v, bool):
            return v
        if v in [None, ""]:
            return SettingsDefaults.DEBUG_MODE
        return v.lower() in ["true", "1", "t", "y", "yes"]

    @field_validator("dump_defaults")
    def parse_dump_defaults(cls, v) -> bool:
        """Parse dump_defaults"""
        if isinstance(v, bool):
            return v
        if v in [None, ""]:
            return SettingsDefaults.DUMP_DEFAULTS
        return v.lower() in ["true", "1", "t", "y", "yes"]

    @field_validator("openai_endpoint_image_n")
    def check_openai_endpoint_image_n(cls, v) -> int:
        """Check openai_endpoint_image_n"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.OPENAI_ENDPOINT_IMAGE_N
        return int(v)

    @field_validator("openai_endpoint_image_size")
    def check_openai_endpoint_image_size(cls, v) -> str:
        """Check openai_endpoint_image_size"""
        if v in [None, ""]:
            return SettingsDefaults.OPENAI_ENDPOINT_IMAGE_SIZE
        return v

    @field_validator("llm_default_model")
    def check_openai_default_model(cls, v) -> str:
        """Check llm_default_model"""
        if v in [None, ""]:
            return SettingsDefaults.LLM_DEFAULT_MODEL
        return v

    @field_validator("llm_default_provider")
    def check_openai_default_provider(cls, v) -> str:
        """Check llm_default_provider"""
        if v in [None, ""]:
            return SettingsDefaults.LLM_DEFAULT_PROVIDER
        return v

    @field_validator("llm_default_system_role")
    def check_openai_default_system_prompt(cls, v) -> str:
        """Check llm_default_system_role"""
        if v in [None, ""]:
            return SettingsDefaults.LLM_DEFAULT_SYSTEM_ROLE
        return v

    @field_validator("llm_default_temperature")
    def check_openai_default_temperature(cls, v) -> float:
        """Check llm_default_temperature"""
        if isinstance(v, float):
            return v
        if v in [None, ""]:
            return SettingsDefaults.LLM_DEFAULT_TEMPERATURE
        return float(v)

    @field_validator("llm_default_max_tokens")
    def check_openai_default_max_tokens(cls, v) -> int:
        """Check llm_default_max_tokens"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.LLM_DEFAULT_MAX_TOKENS
        return int(v)

    @field_validator("smarter_default_cache_timeout")
    def check_smarter_default_cache_timeout(cls, v) -> int:
        """Check smarter_default_cache_timeout"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.SMARTER_DEFAULT_CACHE_TIMEOUT
        retval = int(v)
        if retval < 0:
            raise ValueError("Cache timeout must be greater than or equal to 0")
        return retval

    @field_validator("smarter_max_cache_size")
    def check_smarter_max_cache_size(cls, v) -> int:
        """Check smarter_max_cache_size"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.SMARTER_MAX_CACHE_SIZE
        retval = int(v)
        if retval < 0:
            raise ValueError("Cache size must be greater than or equal to 0")
        return retval

    @field_validator("smarter_default_http_timeout")
    def check_smarter_default_http_timeout(cls, v) -> int:
        """Check smarter_default_http_timeout"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.SMARTER_DEFAULT_HTTP_TIMEOUT
        retval = int(v)
        if retval < 0:
            raise ValueError("HTTP timeout must be greater than or equal to 0")
        return retval


class SingletonSettings:
    """
    Alternative Singleton pattern to resolve metaclass inheritance conflict
    from Pydantic BaseSettings.

    Traceback (most recent call last):
    File "/smarter/manage.py", line 8, in <module>
        from smarter.common.conf import settings as smarter_settings
    File "/smarter/smarter/common/conf.py", line 262, in <module>
        class Settings(BaseSettings, metaclass=Singleton):
    TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict)
               subclass of the metaclasses of all its bases
    """

    _instance = None

    def __new__(cls):
        """Create a new instance of Settings"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                cls._instance._settings = Settings()
            except ValidationError as e:
                raise SmarterConfigurationError("Invalid configuration: " + str(e)) from e
        return cls._instance

    @property
    def settings(self) -> Settings:
        """Return the settings"""
        return self._settings


settings = SingletonSettings().settings
settings_module = "smarter.settings." + settings.environment
importlib.import_module(settings_module)
