"""Models of secrets, prompt history, proxies, orchestrators and vectorsearches."""

from datetime import datetime
from typing import Optional, Union

from pydantic import Field

from smarter.core.typing import SmarterJsonObjectType, SmarterJsonType

from .base import SmarterCamelModel, SmarterModel, SmarterResource
from .plugin import Plugin


class Secret(SmarterResource):
    """A secret's metadata.

    The api never returns a secret's value.
    """

    expires_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None


class Orchestrator(SmarterResource):
    """An orchestrator: a multi-agent workflow that composes LLMClients."""

    strategy: Optional[str] = Field(
        None, description="How its LLMClients collaborate: sequential, parallel, supervisor, router, voting or debate."
    )
    max_iterations: Optional[int] = None
    is_active: Optional[bool] = None
    llmclients: list[int] = Field(default_factory=list, description="The ids of its LLMClients.")


class Vectorsearch(SmarterResource):
    """A vectorsearch: a retrieval pipeline over a vectorstore."""

    search_type: Optional[str] = Field(None, description="similarity, similarity_score_threshold or mmr.")
    k: Optional[int] = Field(None, description="The number of chunks to return.")
    score_threshold: Optional[float] = None
    fetch_k: Optional[int] = Field(None, description="The candidates of an mmr search.")
    lambda_mult: Optional[float] = Field(None, description="An mmr search's diversity.")
    metadata_filter: Optional[SmarterJsonType] = None
    is_enabled: Optional[bool] = None
    vectorstore: Optional[int] = Field(None, description="The id of its vectorstore.")
    auth_secret: Optional[int] = Field(None, description="The id of its Secret, if any.")


class PromptSession(SmarterModel):
    """A chat session: one conversation with an LLMClient, by its session key."""

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    name: Optional[str] = None
    description: Optional[str] = None
    session_key: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    url: Optional[str] = None
    user_profile: Optional[int] = None
    llmclient: Optional[int] = None


class PromptToolCall(SmarterModel):
    """A tool call that the LLM made in a chat session."""

    id: int
    prompt: Union[PromptSession, int, None] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    plugin: Optional[int] = Field(None, description="The id of the plugin that the tool belongs to, if any.")
    function_name: Optional[str] = None
    function_args: Optional[str] = None
    request: SmarterJsonType = None
    response: SmarterJsonType = None


class PromptPluginUsage(SmarterModel):
    """A use of a plugin in a chat session."""

    id: int
    prompt: Union[PromptSession, int, None] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    plugin: Optional[Plugin] = None
    input_text: Optional[str] = None


class Proxy(SmarterCamelModel):
    """
    A proxy: authenticated passthrough access to an LLM provider's own api.

    The platform holds the provider's api key. Callers use their Smarter api key instead, and may
    reach only the proxy's ``allowed_paths``.
    """

    name: str
    description: Optional[str] = None
    provider: Optional[str] = None
    url: Optional[str] = Field(None, description="The proxy's base url on the Smarter platform.")
    upstream_url: Optional[str] = None
    allowed_paths: list[str] = []
    is_active: Optional[bool] = None


class Proxies(SmarterModel):
    """The proxies that the user may call."""

    proxies: list[Proxy] = []


class Provider(SmarterCamelModel):
    """An LLM provider that the platform is configured for, e.g. openai."""

    name: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProviderModel(SmarterCamelModel):
    """A model of an LLM provider."""

    name: str
    description: Optional[str] = None
    max_tokens: Optional[int] = None
    supports_streaming: Optional[bool] = None
    supports_tools: Optional[bool] = None
    metadata: Optional[SmarterJsonObjectType] = None


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
