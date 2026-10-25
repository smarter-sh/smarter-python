"""Models of LLMClients and their plugins, MCPClients, guardrails, extensions, api keys and custom domains."""

from datetime import datetime

from pydantic import Field

from .base import SmarterCamelModel, SmarterResource
from .plugin import Plugin


class LLMClientPluginRef(SmarterCamelModel):
    """A plugin of an LLMClient, by its id and name."""

    id: int
    name: str | None = None


class LLMClientMCPClientRef(SmarterCamelModel):
    """An MCPClient of an LLMClient, by the link's id and the MCPClient's name."""

    id: int
    name: str | None = None


class LLMClientGuardrailRef(SmarterCamelModel):
    """A guardrail of an LLMClient, by the link's id and the guardrail's name."""

    id: int
    name: str | None = None


class LLMClientTool(SmarterCamelModel):
    """Something that an LLMClient adds to a prompt: an extension, plugin, MCPClient or guardrail."""

    id: int = Field(
        ..., description="The id of the link row: the LLMClient's extension, plugin, MCPClient or guardrail."
    )
    name: str = Field(..., description="The extension's slug, or the linked resource's name.")
    kind: str = Field(
        ..., description="Extension, or the linked resource's manifest kind: Plugin, MCPClient or Guardrail."
    )


class LLMClientExtension(SmarterCamelModel):
    """An extension of an LLMClient, whose tools the LLMClient offers the LLM, e.g. ``calculator``."""

    id: int
    name: str | None = Field(None, description="The extension's slug, e.g. weather.")
    extension: int | None = Field(None, description="The Extension's id.")
    llmclient: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class LLMClientPlugin(SmarterCamelModel):
    """The association of a plugin with an LLMClient."""

    id: int
    plugin_meta: Plugin
    llmclient: int | None = None


class LLMClientApiKey(SmarterCamelModel):
    """An api key that may call an LLMClient that requires authentication."""

    id: int
    llmclient: int | None = None
    api_key: str | None = Field(None, description="The api key's public key_id, a UUID. Never the key itself.")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class LLMClientCustomDomain(SmarterCamelModel):
    """A custom domain on which an LLMClient is deployed: the domain itself, and its verification."""

    id: int
    name: str | None = None
    description: str | None = None
    version: str | None = None
    domain_name: str | None = Field(None, description="The domain, e.g. example.com.")
    verification_status: str | None = Field(None, description="Not Verified, Verifying, Verified or Failed.")
    verified_at: datetime | None = None
    verification_message: str | None = None
    user_profile: int | None = Field(None, description="The owner's user profile id.")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class LLMClient(SmarterResource):
    """
    An LLMClient: a deployable AI agent, built from an LLM provider and model, a system prompt, plugins and extensions.

    Prompt it with :meth:`smarter.resources.llmclients.LLMClients.prompt`, or start a chat with
    :meth:`smarter.resources.llmclients.LLMClients.chat`.
    """

    rfc1034_compliant_name: str | None = None
    provider: str | None = None
    default_model: str | None = None
    default_system_role: str | None = Field(None, description="The system prompt of a new chat session.")
    deployed: bool | None = None
    default_host: str | None = None
    default_url: str | None = None
    custom_host: str | None = None
    custom_url: str | None = None
    sandbox_host: str | None = None
    sandbox_url: str | None = None
    url_llmclient: str | None = Field(None, description="Where to send prompts: the chat api's prompt url.")
    url_chat_config: str | None = Field(None, description="The chat api's configuration url.")
    ready: bool | None = Field(None, description="Whether the LLMClient can be prompted.")
    is_authentication_required: bool | None = Field(
        None, description="Whether prompting the LLMClient requires an api key."
    )
    can_delete: bool | None = Field(None, description="Whether the api key's user may delete the LLMClient now.")
    extensions: list[LLMClientExtension] = []
    plugins: list[LLMClientPluginRef] = []
    mcpclients: list[LLMClientMCPClientRef] = []
    guardrails: list[LLMClientGuardrailRef] = []
    tools: list[LLMClientTool] = Field(
        default_factory=list,
        description="Everything that the LLMClient adds to a prompt: its extensions, plugins, MCPClients and "
        "guardrails, in that order.",
    )
    api_keys: list[LLMClientApiKey] = []
    custom_domains: list[LLMClientCustomDomain] = []


__all__ = [
    "LLMClient",
    "LLMClientApiKey",
    "LLMClientCustomDomain",
    "LLMClientExtension",
    "LLMClientGuardrailRef",
    "LLMClientMCPClientRef",
    "LLMClientPlugin",
    "LLMClientPluginRef",
    "LLMClientTool",
]
