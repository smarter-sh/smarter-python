"""
Models of the platform's extensions, as ``/api/v1/extensions/`` returns them.

An extension is a package of LLM tools that a superuser installs on the platform, from the Smarter
extension registry or from a .zip archive, and that LLMClients then use. See
:class:`smarter.resources.extensions.Extensions`. The extensions of one LLMClient are
:class:`~smarter.models.llmclient.LLMClientExtension`.
"""

from datetime import datetime
from typing import Union

from pydantic import Field

from smarter.core.typing import SmarterJsonType

from .base import SmarterCamelModel

ExtensionSettingValue = Union[str, bool, int, float, None]
"""The value of an extension's setting: a string, a boolean, a number, or None for its default."""


class ExtensionAccount(SmarterCamelModel):
    """An account that may use an extension."""

    id: int
    account_number: str
    company_name: str | None = None


class ExtensionSecret(SmarterCamelModel):
    """A Secret of the platform's admin, which an extension's secret setting can use."""

    id: int
    name: str


class ExtensionTool(SmarterCamelModel):
    """One of an extension's tools, as the LLM sees it."""

    name: str = Field(..., description="The tool's name in the extension, e.g. get_weather.")
    function_name: str = Field(..., description="The name that the LLM sees, e.g. ext_weather_get_weather.")
    description: str | None = None
    parameters: SmarterJsonType = Field(None, description="The JSON Schema of the tool's arguments.")


class ExtensionSetting(SmarterCamelModel):
    """One of an extension's settings: its declaration, and its configured value."""

    name: str
    type: str = Field(..., description="string, integer, float, boolean, url, choice or secret.")
    description: str | None = None
    required: bool = False
    default: ExtensionSettingValue = None
    choices: list[str] | None = None
    value: ExtensionSettingValue = Field(None, description="The configured value. Always None for a secret setting.")
    secret_id: int | None = Field(None, description="The id of a secret setting's Secret.")
    secret_name: str | None = Field(None, description="The name of a secret setting's Secret.")
    is_set: bool = Field(False, description="Whether the setting has a configured value, or a Secret.")


class ExtensionVersion(SmarterCamelModel):
    """One installed version of an extension."""

    id: int = Field(..., description="The version's id, for rollback().")
    version: str
    sha256: str | None = None
    source_url: str | None = None
    installed_by: str | None = Field(
        None, description="The username of the superuser who installed it. Only superusers see it."
    )
    created_at: datetime | None = None
    is_installed: bool = Field(False, description="Whether it is the version that runs.")


class ExtensionResource(SmarterCamelModel):
    """A resource, e.g. a Secret or an LLMClient, that an extension created."""

    kind: str
    name: str
    owner: str | None = Field(None, description="The username of the resource's owner.")
    version: str | None = Field(None, description="The extension version that created or last applied it.")
    managed: bool | None = Field(None, description="Whether it came from the package's manifests/ directory.")


class ExtensionSwitch(SmarterCamelModel):
    """A waffle switch that an extension owns."""

    name: str = Field(..., description="The switch's full name, e.g. ext_weather_verbose.")
    description: str | None = None
    active: bool


class ExtensionSummary(SmarterCamelModel):
    """An installed extension, as the platform lists it."""

    id: int
    slug: str = Field(..., description="The extension's slug, e.g. weather.")
    display_name: str
    description: str | None = None
    publisher: str | None = Field(None, description="The publisher's registry id, or an uploaded archive's authors.")
    source: str = Field(..., description="registry or upload.")
    trust_badge: str | None = Field(None, description="official, verified, community or unverified.")
    trust_badge_label: str | None = Field(None, description="The badge, as people read it.")
    enabled: bool
    installed_version: str | None = None
    latest_version: str | None = Field(None, description="The newest compatible version in the registry.")
    update_available: bool = False
    latest_checked_at: datetime | None = None
    error: str = Field("", description="The last error from loading the extension or running its lifecycle hooks.")
    detail_url: str | None = Field(None, description="The url of the extension's page in the web console.")


class ExtensionDetail(ExtensionSummary):
    """
    An installed extension, with its documentation, tools, settings, versions, resources, switches and availability.

    A user who is not a superuser gets it without its settings, the accounts that may use it, the
    platform admin's Secrets, or who installed each version.
    """

    homepage: str | None = None
    license: str | None = None
    docs_html: str = Field("", description="The extension's documentation, as HTML rendered safely.")
    load_error: str | None = Field(None, description="Why the extension's code does not load, if it does not.")
    tools: list[ExtensionTool] = []
    settings: list[ExtensionSetting] = []
    missing_settings: list[str] = Field(
        default_factory=list, description="Required settings that block enabling the extension."
    )
    versions: list[ExtensionVersion] = []
    resources: list[ExtensionResource] = []
    switches: list[ExtensionSwitch] = []
    all_accounts: bool = Field(True, description="Whether every account may use it.")
    accounts: list[ExtensionAccount] = Field(
        default_factory=list, description="The accounts that may use it, when not all accounts may."
    )
    available_secrets: list[ExtensionSecret] = Field(
        default_factory=list, description="The platform admin's Secrets, for secret settings."
    )


class ExtensionList(SmarterCamelModel):
    """The installed extensions that the user may see, and the state of the registry."""

    objects: list[ExtensionSummary] = []
    registry_enabled: bool = Field(False, description="Whether the registry's public key is configured.")
    updates_available: int = Field(0, description="How many installed extensions have an update in the registry.")


class ExtensionDetailResponse(SmarterCamelModel):
    """The response of ``GET /api/v1/extensions/<slug>/``: the extension."""

    extension: ExtensionDetail


class ExtensionRegistryVersion(SmarterCamelModel):
    """A released version of an extension in the registry."""

    version: str
    requires_smarter: str | None = Field(None, description="The Smarter versions it works with, e.g. >=0.27.")
    released_at: datetime | None = None
    compatible: bool = Field(..., description="Whether it works with this platform's Smarter version.")


class ExtensionRegistryEntry(SmarterCamelModel):
    """An extension in the registry, and what it offers this platform."""

    slug: str
    display_name: str
    description: str | None = None
    publisher: str | None = Field(None, description="The publisher's name.")
    publisher_url: str | None = None
    trust_badge: str | None = Field(None, description="official, verified, community or unverified.")
    trust_badge_label: str | None = None
    homepage: str | None = None
    license: str | None = None
    docs_html: str = Field("", description="The extension's documentation, as HTML rendered safely.")
    latest_version: str | None = Field(None, description="The newest version compatible with this platform.")
    versions: list[ExtensionRegistryVersion] = Field(
        default_factory=list, description="Every released version, newest first."
    )
    installed_version: str | None = None
    action: str = Field(..., description="install, update, installed, uploaded or incompatible.")
    detail_url: str | None = Field(None, description="The installed extension's page, if it is installed.")


class ExtensionRegistry(SmarterCamelModel):
    """The registry's extensions, or why they cannot be listed."""

    enabled: bool = Field(..., description="Whether the registry's public key is configured.")
    error: str | None = Field(None, description="Why the registry cannot be read, if it cannot.")
    objects: list[ExtensionRegistryEntry] = []


class ExtensionActionResult(SmarterCamelModel):
    """The result of an action on extensions: what happened, and the extension as it now is."""

    message: str
    extension: ExtensionDetail | None = Field(
        None, description="The extension, or None after uninstall() and check_updates()."
    )


__all__ = [
    "ExtensionAccount",
    "ExtensionActionResult",
    "ExtensionDetail",
    "ExtensionDetailResponse",
    "ExtensionList",
    "ExtensionRegistry",
    "ExtensionRegistryEntry",
    "ExtensionRegistryVersion",
    "ExtensionResource",
    "ExtensionSecret",
    "ExtensionSetting",
    "ExtensionSettingValue",
    "ExtensionSummary",
    "ExtensionSwitch",
    "ExtensionTool",
    "ExtensionVersion",
]
