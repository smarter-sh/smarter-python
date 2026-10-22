"""
SAM model of the ``ApiConnection`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional, Union
from uuid import UUID

from pydantic import Field, conint

from smarter.models.sam.base import SAMModel


class ApiConnection(SAMModel):
    """Smarter API - generic API Connection class."""

    apiKey: str | None = Field(None, title="Apikey")
    """The API key for authentication, if required."""
    authMethod: str | None = Field("none", title="Authmethod")
    """
    The authentication method to use.

    Example: 'Basic Auth', 'Token Auth'.
    """
    baseUrl: str = Field(..., title="Baseurl")
    """
    The root domain of the API.

    Example: 'https://api.example.com'.
    """
    proxyHost: str | None = Field(None, title="Proxyhost")
    """The remote host of the proxy connection."""
    proxyPassword: str | None = Field(None, title="Proxypassword")
    """The password for the proxy connection."""
    proxyPort: int | None = Field(None, title="Proxyport")
    """The port of the proxy connection."""
    proxyProtocol: str | None = Field(None, title="Proxyprotocol")
    """
    The protocol of the proxy connection.

    Example: 'http', 'https'.
    """
    proxyUsername: str | None = Field(None, title="Proxyusername")
    """The username for the proxy connection."""
    timeout: conint(ge=1) | None = Field(30, title="Timeout")
    """
    The timeout for the API request in seconds.

    Default is 30 seconds.
    """


class SAMApiConnectionSpec(SAMModel):
    """Smarter API Api Connection Manifest ApiConnection.spec."""

    connection: ApiConnection
    """ApiConnection.spec.selector[obj]: the selector logic to use for the ApiConnection."""


class SAMConnectionCommonMetadata(SAMModel):
    """Smarter API Connection Manifest - common Metadata class."""

    annotations: None | (
        list[dict[str, str | int | float | bool | date | datetime | UUID | bytes | list | dict[str, Any]]]
    ) = Field(None, title="Annotations")
    """
    The manifest annotations.

    Used for storing arbitrary metadata as
                key-value pairs. Example: [{'smarter.sh/test-manifest/project-name': 'Scooby dooby do'}]. The
                key should be a valid url-friendly string. The value accepts
                multi-line string values (YAML block scalars) and various scalar types including
                str, int, float, bool, datetime.date, datetime.datetime, decimal.Decimal, uuid.UUID, bytes, list, dict.
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


class SAMConnectionCommonStatus(SAMModel):
    """Smarter API Connection Manifest - Status class."""

    account_number: str = Field(..., title="Account Number")
    """
    Connection.status.account_number: The account owner of this Connection.

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
    username: str = Field(..., title="Username")
    """
    Connection.status.username: The Smarter user who created this Connection.

    Read only.
    """


class SAMApiConnection(SAMModel):
    """Smarter API Connection Manifest - ApiConnection Model."""

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
    metadata: SAMConnectionCommonMetadata
    """Connection.metadata[obj]: Required, the Connection metadata."""
    spec: SAMApiConnectionSpec
    """ApiConnection.spec[obj]: Required, the ApiConnection specification."""
    status: SAMConnectionCommonStatus | None = None
    """
    Connection.status[obj]: Optional, Read-only.

    Stateful status information about the Connection.
    """
