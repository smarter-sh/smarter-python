"""
SAM model of the ``SmarterAuthToken`` kind, generated from the Smarter platform's JSON Schema.

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


class SAMSmarterAuthTokenMetadata(SAMModel):
    """Smarter API SmarterAuthToken Manifest - Metadata class."""

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


class SAMSmarterAuthTokenSpecConfig(SAMModel):
    """Smarter API SmarterAuthToken Manifest SmarterAuthToken.spec.config."""

    isActive: bool | None = Field(False, title="Isactive")
    """
    SmarterAuthToken.spec.configuration.isActive[bool].

    Required. Whether the SmarterAuthToken is activated.
    """
    username: str = Field(..., title="Username")
    """
    SmarterAuthToken.spec.configuration.username[str].

    The Smarter username to which this SmarterAuthToken is attached.
    """


class SAMSmarterAuthTokenStatus(SAMModel):
    """Smarter API SmarterAuthToken Manifest - Status class."""

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
    lastUsedAt: datetime | None = Field(None, title="Lastusedat")
    """
    SmarterAuthToken.status.modified: The date in which this SmarterAuthToken was most recently used for authentication.

    Read only.
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


class SAMSmarterAuthTokenSpec(SAMModel):
    """Smarter API SmarterAuthToken Manifest SmarterAuthToken.spec."""

    config: SAMSmarterAuthTokenSpecConfig
    """
    SmarterAuthToken.spec.config[object].

    The configuration for the SmarterAuthToken.
    """


class SAMSmarterAuthToken(SAMModel):
    """Smarter API Manifest - SmarterAuthToken."""

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
    metadata: SAMSmarterAuthTokenMetadata
    """SmarterAuthToken.metadata[obj]: Required, the SmarterAuthToken metadata."""
    spec: SAMSmarterAuthTokenSpec
    """SmarterAuthToken.spec[obj]: Required, the SmarterAuthToken specification."""
    status: SAMSmarterAuthTokenStatus | None = None
    """
    SmarterAuthToken.status[obj]: Optional, Read-only.

    Stateful status information about the SmarterAuthToken.
    """
