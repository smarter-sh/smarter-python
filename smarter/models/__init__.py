"""
The SDK's models of the Smarter api's requests and responses.

Every model is a Pydantic model that keeps fields it does not declare, so that the SDK keeps
working when the platform adds fields. See :mod:`smarter.models.base`.

- :mod:`smarter.models.sam`: a typed model of every SAM manifest kind, e.g. ``SAMLLMClient``
- :mod:`smarter.models.chat`: the Smarter Chat api contract, e.g. ``PromptChatApiConfig``
- :mod:`smarter.models.journal`: the Smarter Journal api contract
- :mod:`smarter.models.react`: the Django-React integration contract, e.g. ``ViteManifest``
- the other modules: the REST api's resources, e.g. ``LLMClient`` and ``Guardrail``
"""

from .account import Account, AccountContact, User, UserProfile
from .base import SmarterModel, SmarterResource
from .chat import (
    PromptChatApiConfig,
    PromptChatApiMessage,
    PromptChatApiProgressEvent,
    PromptChatApiPromptResponse,
    PromptChatApiPromptResult,
)
from .guardrail import Guardrail, GuardrailEvaluation, GuardrailEvent, GuardrailEvents
from .journal import (
    JournalEntry,
    JournalPage,
    SAMJournalApiErrorBody,
    SmarterJournaledResponse,
)
from .llmclient import (
    LLMClient,
    LLMClientApiKey,
    LLMClientCustomDomain,
    LLMClientFunction,
    LLMClientPlugin,
)
from .llmhost import (
    DiscoveredModel,
    DiscoveredModels,
    LLMHost,
    LLMHostLogs,
    LLMHostPlan,
    LLMHostReport,
    LLMHostStatus,
)
from .manifest import KindInfo, Manifest, ManifestList, ManifestMetadata
from .mcpclient import (
    MCPClient,
    MCPClientStatus,
    MCPClientTools,
    MCPTool,
    MCPToolResult,
)
from .misc import (
    Orchestrator,
    PromptPluginUsage,
    PromptSession,
    PromptToolCall,
    Provider,
    ProviderModel,
    Proxy,
    Secret,
    Vectorsearch,
)
from .platform import PlatformStatus, PlatformVersion, WhoAmI
from .plugin import Plugin
from .react import ReactAppAssets, ReactAppBuildInfo, ViteManifest, ViteManifestChunk
from .vectorstore import (
    Vectorstore,
    VectorstoreDocument,
    VectorstoreDocumentDeleted,
    VectorstoreDocuments,
    VectorstoreDocumentsAdded,
    VectorstoreRestored,
    VectorstoreSearchResult,
    VectorstoreSearchResults,
    VectorstoreSnapshot,
    VectorstoreSnapshots,
    VectorstoreStatus,
)

__all__ = [
    "Account",
    "AccountContact",
    "DiscoveredModel",
    "DiscoveredModels",
    "Guardrail",
    "GuardrailEvaluation",
    "GuardrailEvent",
    "GuardrailEvents",
    "JournalEntry",
    "JournalPage",
    "KindInfo",
    "LLMClient",
    "LLMClientApiKey",
    "LLMClientCustomDomain",
    "LLMClientFunction",
    "LLMClientPlugin",
    "LLMHost",
    "LLMHostLogs",
    "LLMHostPlan",
    "LLMHostReport",
    "LLMHostStatus",
    "MCPClient",
    "MCPClientStatus",
    "MCPClientTools",
    "MCPTool",
    "MCPToolResult",
    "Manifest",
    "ManifestList",
    "ManifestMetadata",
    "Orchestrator",
    "PlatformStatus",
    "PlatformVersion",
    "Plugin",
    "PromptChatApiConfig",
    "PromptChatApiMessage",
    "PromptChatApiProgressEvent",
    "PromptChatApiPromptResponse",
    "PromptChatApiPromptResult",
    "PromptPluginUsage",
    "PromptSession",
    "PromptToolCall",
    "ReactAppAssets",
    "ReactAppBuildInfo",
    "Provider",
    "ProviderModel",
    "Proxy",
    "SAMJournalApiErrorBody",
    "Secret",
    "SmarterJournaledResponse",
    "SmarterModel",
    "SmarterResource",
    "User",
    "UserProfile",
    "Vectorsearch",
    "Vectorstore",
    "VectorstoreDocument",
    "VectorstoreDocumentDeleted",
    "VectorstoreDocuments",
    "VectorstoreDocumentsAdded",
    "VectorstoreRestored",
    "VectorstoreSearchResult",
    "VectorstoreSearchResults",
    "VectorstoreSnapshot",
    "VectorstoreSnapshots",
    "VectorstoreStatus",
    "ViteManifest",
    "ViteManifestChunk",
    "WhoAmI",
]
