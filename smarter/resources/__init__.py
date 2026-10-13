"""
The api resources of a :class:`smarter.Smarter` client.

Each is an attribute of the client, e.g. ``client.llm_clients`` or ``client.manifests``.
"""

from .accounts import AccountContacts, Accounts, Users
from .base import ManifestInput, SmarterAPIResource, SmarterKindResource
from .catalog import Orchestrators, Plugins, Secrets, Vectorsearches
from .guardrails import Guardrails
from .history import Journal, PromptHistory
from .llmclients import (
    ChatSession,
    ChatStream,
    LLMClients,
    PromptStream,
    SmarterPromptError,
)
from .llmhosts import LLMHosts
from .manifests import Manifests, ManifestValidation
from .mcpclients import MCPClients
from .providers import Providers
from .proxies import Proxies
from .vectorstores import Vectorstores

__all__ = [
    "AccountContacts",
    "Accounts",
    "ChatSession",
    "ChatStream",
    "Guardrails",
    "Journal",
    "LLMClients",
    "LLMHosts",
    "MCPClients",
    "ManifestInput",
    "ManifestValidation",
    "Manifests",
    "Orchestrators",
    "Plugins",
    "PromptHistory",
    "PromptStream",
    "Providers",
    "Proxies",
    "Secrets",
    "SmarterAPIResource",
    "SmarterKindResource",
    "SmarterPromptError",
    "Users",
    "Vectorsearches",
    "Vectorstores",
]
