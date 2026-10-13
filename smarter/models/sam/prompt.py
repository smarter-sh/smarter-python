"""
SAM model of the ``Prompt`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional, Union
from uuid import UUID

from pydantic import Field, constr

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


class SAMPromptMetadata(SAMModel):
    """Smarter API Prompt Manifest - Metadata class."""

    annotations: None | (
        list[
            dict[
                str,
                (
                    str
                    | int
                    | float
                    | bool
                    | date
                    | datetime
                    | constr(pattern=r"^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$")
                    | UUID
                    | bytes
                    | list
                    | dict[str, Any]
                ),
            ]
        ]
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


class SAMPromptSpecConfig(SAMModel):
    """Smarter API Prompt Manifest Prompt.spec.config."""

    ipAddress: str | None = Field(None, title="Ipaddress")
    """
    Prompt.spec.configuration.ipAddress[str].

    Read only. The IP address of the client that started the chat session.
    """
    llmclient: str | None = Field(None, title="Llmclient")
    """
    Prompt.spec.configuration.llmclient[str].

    Read only. The name of the LLMClient of the chat session.
    """
    sessionKey: str | None = Field(None, title="Sessionkey")
    """
    Prompt.spec.configuration.sessionKey[str].

    Read only. The session key of the Prompt's chat session.
    """
    url: str | None = Field(None, title="Url")
    """
    Prompt.spec.configuration.url[str].

    Read only. The url at which the chat session was started.
    """
    userAgent: str | None = Field(None, title="Useragent")
    """
    Prompt.spec.configuration.userAgent[str].

    Read only. The user agent of the client that started the chat session.
    """


class SAMPromptStatus(SAMModel):
    """Smarter API Prompt Manifest - Status class."""

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


class SAMPrompt(SAMModel):
    """Smarter API Manifest - Prompt."""

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
    metadata: SAMPromptMetadata
    """Prompt.metadata[obj]: Required, the Prompt metadata."""
    spec: SAMPromptSpecConfig
    """Prompt.spec[obj]: Required, the Prompt specification."""
    status: SAMPromptStatus | None = None
    """
    Prompt.status[obj]: Optional, Read-only.

    Stateful status information about the Prompt.
    """
