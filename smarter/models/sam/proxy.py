"""
SAM model of the ``Proxy`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import ConfigDict, Field, conint

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


class SAMProxyMetadata(SAMModel):
    """Smarter API Proxy Manifest - Metadata class."""

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


class SAMProxySpecAuth(SAMModel):
    """Spec.auth: how the provider expects its API key."""

    model_config = ConfigDict(
        extra="forbid",
    )
    header: str | None = Field("Authorization", title="Header")
    """Proxy.spec.auth.header[str]: the HTTP header in which the provider expects its API key, e.g. Authorization (OpenAI), x-api-key (Anthropic) or x-goog-api-key (Google Gemini)."""
    scheme: str | None = Field("Bearer", title="Scheme")
    """
    Proxy.spec.auth.scheme[str]: the prefix of the API key in the header, e.g. Bearer.

    Empty or null for none, e.g. for x-api-key.
    """


class SAMProxyStatus(SAMModel):
    """
    Smarter API Proxy Manifest - Status class.

    Read only. Besides ownership, it reports where the Proxy is, and where it forwards to.
    """

    accountNumber: str = Field(..., title="Accountnumber")
    """
    Proxy.status.accountNumber: The account owner of this Proxy.

    Read only.
    """
    apiKeySecret: str | None = Field(None, title="Apikeysecret")
    """
    Proxy.status.apiKeySecret: The name of the Secret whose API key is added to requests: spec.apiKey, else the Provider's.

    None if there is none. Read only.
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
    modified: datetime = Field(..., title="Modified")
    """
    The date in which this resource was most recently changed.

    Read only.
    """
    recordLocator: str = Field(..., title="Recordlocator")
    """
    RecordLocator[String]: An optional identifier used to locate the resource record associated with this manifest.

    Read only.
    """
    upstreamUrl: str | None = Field(None, title="Upstreamurl")
    """
    Proxy.status.upstreamUrl: The base URL of the provider's API, to which requests are forwarded: spec.baseUrl, else the Provider's.

    Read only.
    """
    url: str | None = Field(None, title="Url")
    """
    Proxy.status.url: The URL of the Proxy's passthrough endpoint, to use as the base URL of the provider's SDK.

    Read only.
    """
    username: str = Field(..., title="Username")
    """
    Proxy.status.username: The Smarter user who created this Proxy.

    Read only.
    """


class SAMProxySpec(SAMModel):
    """Smarter API Proxy Manifest Proxy.spec."""

    model_config = ConfigDict(
        extra="forbid",
    )
    allowedPaths: list[str] | None = Field(None, title="Allowedpaths")
    """
    Proxy.spec.allowedPaths[list]: glob patterns of the paths, relative to baseUrl, that callers may use, e.g. chat/completions or models/*.

    Empty allows every path.
    """
    apiKey: str | None = Field(None, title="Apikey")
    """
    Proxy.spec.apiKey[str]: the name of the Secret that contains the provider's API key.

    It must belong to, or be shared with, the manifest's owner. Defaults to the Provider's API key.
    """
    auth: SAMProxySpecAuth | None = None
    """
    Proxy.spec.auth[object]: how the provider expects its API key.

    Defaults to Authorization: Bearer.
    """
    baseUrl: str | None = Field(None, title="Baseurl")
    """
    Proxy.spec.baseUrl[str]: the base URL of the provider's API, e.g. https://api.openai.com/v1/.

    Defaults to the Provider's base URL.
    """
    headers: dict[str, str] | None = Field(None, title="Headers")
    """
    Proxy.spec.headers[dict]: other HTTP headers that are added to every request, e.g. anthropic-version.

    They replace the caller's headers of the same name.
    """
    isActive: bool | None = Field(True, title="Isactive")
    """Proxy.spec.isActive[bool]: inactive Proxy refuse every request."""
    provider: str = Field(..., title="Provider")
    """
    Proxy.spec.provider[str]: the name of the Provider whose API the Proxy forwards to, e.g. openai.

    It must belong to, or be shared with, the manifest's owner.
    """
    timeout: conint(ge=1, le=600) | None = Field(120, title="Timeout")
    """Proxy.spec.timeout[int]: the most seconds to wait for the provider's response."""


class SAMProxy(SAMModel):
    """Smarter API Manifest - Proxy."""

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
    metadata: SAMProxyMetadata
    """Proxy.metadata[obj]: Required, the Proxy metadata."""
    spec: SAMProxySpec
    """Proxy.spec[obj]: Required, the Proxy specification."""
    status: SAMProxyStatus | None = None
    """
    Proxy.status[obj]: Optional, Read-only.

    Stateful status information about the Proxy.
    """
