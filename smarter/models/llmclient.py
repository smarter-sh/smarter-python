"""Models of LLMClients and their plugins, built-in functions, api keys and custom domains."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from .base import SmarterCamelModel, SmarterResource
from .plugin import Plugin


class LLMClientPluginRef(SmarterCamelModel):
    """A plugin of an LLMClient, by its id and name."""

    id: int
    name: Optional[str] = None


class LLMClientFunction(SmarterCamelModel):
    """A built-in function of an LLMClient, e.g. ``calculator``."""

    id: int
    name: Optional[str] = None
    llmclient: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LLMClientPlugin(SmarterCamelModel):
    """The association of a plugin with an LLMClient."""

    id: int
    plugin_meta: Plugin
    llmclient: Optional[int] = None


class LLMClientApiKey(SmarterCamelModel):
    """An api key that may call an LLMClient that requires authentication."""

    id: int
    llmclient: Optional[int] = None
    api_key: Optional[str] = Field(None, description="The api key's public key_id, a UUID. Never the key itself.")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LLMClientCustomDomain(SmarterCamelModel):
    """A custom domain on which an LLMClient is deployed: the domain itself, and its verification."""

    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    domain_name: Optional[str] = Field(None, description="The domain, e.g. example.com.")
    verification_status: Optional[str] = Field(None, description="Not Verified, Verifying, Verified or Failed.")
    verified_at: Optional[datetime] = None
    verification_message: Optional[str] = None
    user_profile: Optional[int] = Field(None, description="The owner's user profile id.")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LLMClient(SmarterResource):
    """
    An LLMClient: a deployable AI agent, built from an LLM provider and model, a system prompt, plugins and functions.

    Prompt it with :meth:`smarter.resources.llmclients.LLMClients.prompt`, or start a chat with
    :meth:`smarter.resources.llmclients.LLMClients.chat`.
    """

    rfc1034_compliant_name: Optional[str] = None
    provider: Optional[str] = None
    default_model: Optional[str] = None
    default_system_role: Optional[str] = Field(None, description="The system prompt of a new chat session.")
    deployed: Optional[bool] = None
    default_host: Optional[str] = None
    default_url: Optional[str] = None
    custom_host: Optional[str] = None
    custom_url: Optional[str] = None
    sandbox_host: Optional[str] = None
    sandbox_url: Optional[str] = None
    url_llmclient: Optional[str] = Field(None, description="Where to send prompts: the chat api's prompt url.")
    url_chat_config: Optional[str] = Field(None, description="The chat api's configuration url.")
    ready: Optional[bool] = Field(None, description="Whether the LLMClient can be prompted.")
    is_authentication_required: Optional[bool] = Field(
        None, description="Whether prompting the LLMClient requires an api key."
    )
    can_delete: Optional[bool] = Field(None, description="Whether the api key's user may delete the LLMClient now.")
    functions: list[LLMClientFunction] = []
    plugins: list[LLMClientPluginRef] = []
    api_keys: list[LLMClientApiKey] = []
    custom_domains: list[LLMClientCustomDomain] = []


__all__ = [
    "LLMClient",
    "LLMClientApiKey",
    "LLMClientCustomDomain",
    "LLMClientFunction",
    "LLMClientPlugin",
    "LLMClientPluginRef",
]
