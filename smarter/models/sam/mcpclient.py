"""
SAM model of the ``MCPClient`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field, conint

from smarter.models.sam.base import SAMModel


class SAMDependency(SAMModel):
    """A resource that depends on the resource that a manifest describes."""

    kind: str = Field(..., title="Kind")
    """
    Kind[String]: The SAM kind of the resource that depends on this resource, e.g. LLMClient.

    Read only.
    """
    name: str = Field(..., title="Name")
    """
    Name[String]: The name of the resource that depends on this resource.

    Read only.
    """


class SAMMCPClientMetadata(SAMModel):
    """Smarter API MCPClient Manifest - Metadata class."""

    annotations: dict[str, str] | None = Field(
        None,
        examples=[{"acme.com/crm-account-id": "A-10042", "smarter.sh/llmclient/use-case": "customer support"}],
        title="Annotations",
    )
    """
    Annotations, as in Kubernetes: a map of keys to string values that clients and integrations attach to a resource for their own purposes, e.g. to associate it with a resource in another system.

    A key is an optional DNS-subdomain prefix that names its owner, then a slash and a name of one or more slash-separated segments, e.g. 'acme.com/crm-account-id'. The prefix 'smarter.sh' and its subdomains are reserved for the Smarter platform. Values are strings: unquoted YAML scalars such as true, 42 or dates are converted to strings, and structured data belongs in a JSON string. All annotations together are limited to 256 KiB. The list of one-key maps of older manifests, e.g. [{'acme.com/crm-account-id': 'A-10042'}], is also accepted.
    """
    description: str | None = Field(..., title="Description")
    """
    The description for this resource.

    Be brief. Keep it under 255 characters.
    """
    name: str = Field(..., title="Name")
    """The camelCase name of the manifest resource."""
    tags: list[str] | None = Field(None, title="Tags")
    """
    The tags of the manifest.

    Used for generic resource categorization and search. Example: ['tag1', 'tag2']
    """
    version: str | None = Field(..., title="Version")
    """
    The semantic version of the manifest.

    Example: 0.1.0
    """


class AuthType(Enum):
    """
    MCPClient.spec.config.authType[str]: how to authenticate with the MCP server.

    One of: ['none', 'api_key', 'bearer_token', 'oauth2']. oauth2 sends an OAuth access token, obtained elsewhere, as a bearer token.
    """

    none = "none"
    api_key = "api_key"
    bearer_token = "bearer_token"
    oauth2 = "oauth2"


class Transport(Enum):
    """
    MCPClient.spec.config.transport[str]: the MCP transport.

    One of: ['http', 'sse']. http is Streamable HTTP, and sse is the legacy HTTP+SSE transport.
    """

    http = "http"
    sse = "sse"


class SAMMCPClientSpecConfig(SAMModel):
    """Smarter API MCPClient Manifest MCPClient.spec.config."""

    allowedResources: list[str] | None = Field(None, title="Allowedresources")
    """
    MCPClient.spec.config.allowedResources[list]: glob patterns of the resource URIs that the LLM may read, e.g. docs://example.com/* .

    Empty means none.
    """
    allowedTools: list[str] | None = Field(None, title="Allowedtools")
    """
    MCPClient.spec.config.allowedTools[list]: glob patterns of the tool names to offer the LLM, e.g. search_* .

    Empty means all of the tools that the server advertises.
    """
    apiKeyHeader: str | None = Field("X-API-Key", title="Apikeyheader")
    """MCPClient.spec.config.apiKeyHeader[str]: the HTTP header that carries an api_key credential."""
    authType: AuthType | None = Field("none", title="Authtype")
    """
    MCPClient.spec.config.authType[str]: how to authenticate with the MCP server.

    One of: ['none', 'api_key', 'bearer_token', 'oauth2']. oauth2 sends an OAuth access token, obtained elsewhere, as a bearer token.
    """
    cacheTtl: conint(ge=0, le=86400) | None = Field(3600, title="Cachettl")
    """
    MCPClient.spec.config.cacheTtl[int]: seconds to cache the MCP server's tools, instructions and capabilities, and the results of its read-only tools and resource reads.

    0 disables caching.
    """
    credentials: str | None = Field(None, title="Credentials")
    """
    MCPClient.spec.config.credentials[str]: the name of the Smarter Secret containing the credential.

    Required unless authType is none.
    """
    endpointUrl: str = Field(..., title="Endpointurl")
    """MCPClient.spec.config.endpointUrl[str]: the https URL of the MCP server's endpoint."""
    headers: dict[str, str] | None = Field(None, title="Headers")
    """
    MCPClient.spec.config.headers[dict]: optional, non-secret HTTP headers to send to the MCP server.

    Credentials belong in a Smarter Secret, via credentials.
    """
    includeInstructions: bool | None = Field(True, title="Includeinstructions")
    """MCPClient.spec.config.includeInstructions[bool]: add the MCP server's instructions to the system prompt."""
    isActive: bool | None = Field(True, title="Isactive")
    """MCPClient.spec.config.isActive[bool]: whether LLMClients use this MCPClient."""
    priority: conint(ge=0) | None = Field(100, title="Priority")
    """
    MCPClient.spec.config.priority[int]: the order in which an LLMClient's MCPClients are offered to the LLM.

    Lower runs first.
    """
    timeout: conint(ge=1, le=120) | None = Field(30, title="Timeout")
    """MCPClient.spec.config.timeout[int]: seconds to wait for the MCP server to connect and respond."""
    transport: Transport | None = Field("http", title="Transport")
    """
    MCPClient.spec.config.transport[str]: the MCP transport.

    One of: ['http', 'sse']. http is Streamable HTTP, and sse is the legacy HTTP+SSE transport.
    """


class SAMMCPClientStatus(SAMModel):
    """
    Smarter API MCPClient Manifest - Status class.

    Read only. Besides ownership, it reports the result of the last connection to the MCP server.
    """

    accountNumber: str = Field(..., title="Accountnumber")
    """
    MCPClient.status.account_number: The account owner of this MCPClient.

    Read only.
    """
    connectionStatus: str | None = Field(None, title="Connectionstatus")
    """
    MCPClient.status.connectionStatus: the result of the last connection to the MCP server: unconfigured, connected, disconnected or error.

    Read only.
    """
    created: datetime = Field(..., title="Created")
    """
    The date in which this resource was created.

    Read only.
    """
    dependencies: list[SAMDependency] | None = Field(None, title="Dependencies")
    """
    Dependencies[List]: The resources that depend on this resource, and that must be deleted, or stop referring to it, before it can be deleted.

    Lists only the resources that you can read. Read only.
    """
    lastConnected: datetime | None = Field(None, title="Lastconnected")
    """
    MCPClient.status.lastConnected: when Smarter last connected to the MCP server.

    Read only.
    """
    lastError: str | None = Field(None, title="Lasterror")
    """
    MCPClient.status.lastError: the error of the last failed connection, if any.

    Read only.
    """
    modified: datetime = Field(..., title="Modified")
    """
    The date in which this resource was most recently changed.

    Read only.
    """
    protocolVersion: str | None = Field(None, title="Protocolversion")
    """
    MCPClient.status.protocolVersion: the MCP protocol version negotiated with the server.

    Read only.
    """
    recordLocator: str = Field(..., title="Recordlocator")
    """
    RecordLocator[String]: An optional identifier used to locate the resource record associated with this manifest.

    Read only.
    """
    serverName: str | None = Field(None, title="Servername")
    """
    MCPClient.status.serverName: the name that the MCP server reported.

    Read only.
    """
    serverVersion: str | None = Field(None, title="Serverversion")
    """
    MCPClient.status.serverVersion: the version that the MCP server reported.

    Read only.
    """
    tools: list[str] | None = Field(None, title="Tools")
    """
    MCPClient.status.tools: the names of the MCP server's tools that this MCPClient offers the LLM, as of the last connection.

    Read only.
    """
    username: str = Field(..., title="Username")
    """
    MCPClient.status.username: The Smarter user who created this MCPClient.

    Read only.
    """


class SAMMCPClientSpec(SAMModel):
    """Smarter API MCPClient Manifest MCPClient.spec."""

    config: SAMMCPClientSpecConfig
    """
    MCPClient.spec.config[object].

    The configuration for the MCPClient.
    """


class SAMMCPClient(SAMModel):
    """Smarter API Manifest - MCPClient."""

    apiVersion: str = Field(..., title="Apiversion")
    """
    ApiVersion[String]: Required.

    The API version of the AbstractSAMBase.
    """
    kind: str = Field(..., title="Kind")
    """
    Kind[String]: Required.

    The kind of resource described by the manifest.
    """
    metadata: SAMMCPClientMetadata
    """MCPClient.metadata[obj]: Required, the MCPClient metadata."""
    spec: SAMMCPClientSpec
    """MCPClient.spec[obj]: Required, the MCPClient specification."""
    status: SAMMCPClientStatus | None = None
    """
    MCPClient.status[obj]: Optional, Read-only.

    Stateful status information about the MCPClient.
    """
