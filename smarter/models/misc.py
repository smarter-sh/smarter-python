"""Models of secrets, prompt history, proxies, orchestrators and vectorsearches."""

from datetime import datetime

from pydantic import Field

from smarter.core.typing import SmarterJsonObjectType, SmarterJsonType

from .base import SmarterCamelModel, SmarterModel, SmarterResource
from .plugin import Plugin


class Secret(SmarterResource):
    """A secret's metadata.

    The api never returns a secret's value.
    """

    expires_at: datetime | None = None
    last_accessed: datetime | None = None


class Orchestrator(SmarterResource):
    """An orchestrator: a multi-agent workflow that composes LLMClients."""

    strategy: str | None = Field(
        None, description="How its LLMClients collaborate: sequential, parallel, supervisor, router, voting or debate."
    )
    max_iterations: int | None = None
    is_active: bool | None = None
    llmclients: list[int] = Field(default_factory=list, description="The ids of its LLMClients.")


class Vectorsearch(SmarterResource):
    """A vectorsearch: a retrieval pipeline over a vectorstore."""

    search_type: str | None = Field(None, description="similarity, similarity_score_threshold or mmr.")
    k: int | None = Field(None, description="The number of chunks to return.")
    score_threshold: float | None = None
    fetch_k: int | None = Field(None, description="The candidates of an mmr search.")
    lambda_mult: float | None = Field(None, description="An mmr search's diversity.")
    metadata_filter: SmarterJsonType | None = None
    is_enabled: bool | None = None
    vectorstore: int | None = Field(None, description="The id of its vectorstore.")
    auth_secret: int | None = Field(None, description="The id of its Secret, if any.")


class PromptSession(SmarterModel):
    """A chat session: one conversation with an LLMClient, by its session key."""

    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    name: str | None = None
    description: str | None = None
    session_key: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    url: str | None = None
    user_profile: int | None = None
    llmclient: int | None = None


class PromptToolCall(SmarterModel):
    """A tool call that the LLM made in a chat session."""

    id: int
    prompt: PromptSession | int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    plugin: int | None = Field(None, description="The id of the plugin that the tool belongs to, if any.")
    function_name: str | None = None
    function_args: str | None = None
    request: SmarterJsonType = None
    response: SmarterJsonType = None


class PromptPluginUsage(SmarterModel):
    """A use of a plugin in a chat session."""

    id: int
    prompt: PromptSession | int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    plugin: Plugin | None = None
    input_text: str | None = None


class Proxy(SmarterCamelModel):
    """
    A proxy: authenticated passthrough access to an LLM provider's own api.

    The platform holds the provider's api key. Callers use their Smarter api key instead, and may
    reach only the proxy's ``allowed_paths``.
    """

    name: str
    description: str | None = None
    provider: str | None = None
    url: str | None = Field(None, description="The proxy's base url on the Smarter platform.")
    upstream_url: str | None = None
    allowed_paths: list[str] = []
    is_active: bool | None = None


class Proxies(SmarterModel):
    """The proxies that the user may call."""

    proxies: list[Proxy] = []


class Provider(SmarterCamelModel):
    """An LLM provider that the platform is configured for, e.g. openai."""

    name: str
    description: str | None = None
    base_url: str | None = None
    is_active: bool | None = None


class ProviderModel(SmarterCamelModel):
    """A model of an LLM provider."""

    name: str
    description: str | None = None
    max_tokens: int | None = None
    supports_streaming: bool | None = None
    supports_tools: bool | None = None
    metadata: SmarterJsonObjectType | None = None


__all__ = [
    "Orchestrator",
    "PromptPluginUsage",
    "PromptSession",
    "PromptToolCall",
    "Provider",
    "ProviderModel",
    "Proxies",
    "Proxy",
    "Secret",
    "Vectorsearch",
]
