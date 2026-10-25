"""
SAM model of the ``User`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import Field

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


class SAMUserMetadata(SAMModel):
    """Smarter API User Manifest - Metadata class."""

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
    username: str = Field(..., title="Username")
    """
    User.metadata.username[str].

    Required. The Django username of the user.
    """
    version: str | None = Field(..., title="Version")
    """
    The semantic version of the manifest.

    Example: 0.1.0
    """


class SAMUserSpecConfig(SAMModel):
    """Smarter API User Manifest User.spec.config."""

    email: str = Field(..., title="Email")
    """
    User.spec.configuration.email[str].

    The email address of the User.
    """
    firstName: str | None = Field(None, title="Firstname")
    """
    User.spec.configuration.firstName[str].

    Optional. The first name of the User.
    """
    isActive: bool = Field(..., title="Isactive")
    """
    User.spec.configuration.isActive[bool].

    Designates whether this User should be treated as active.
    """
    isStaff: bool | None = Field(False, title="Isstaff")
    """
    User.spec.configuration.isStaff[bool].

    Optional. Designates whether the User has admin permissions.
    """
    lastName: str | None = Field(None, title="Lastname")
    """
    User.spec.configuration.lastName[str].

    Optional. The last name of the User.
    """


class SAMUserStatus(SAMModel):
    """Smarter API User Manifest - Status class."""

    account_number: str = Field(..., title="Account Number")
    """
    User.status.account_number: The account owner of this User.

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
    User.status.account_number: The Smarter user who created this User.

    Read only.
    """


class SAMUserSpec(SAMModel):
    """Smarter API User Manifest User.spec."""

    config: SAMUserSpecConfig
    """
    User.spec.config[object].

    The configuration for the User.
    """


class SAMUser(SAMModel):
    """Smarter API Manifest - User."""

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
    metadata: SAMUserMetadata
    """User.metadata[obj]: Required, the User metadata."""
    spec: SAMUserSpec
    """User.spec[obj]: Required, the User specification."""
    status: SAMUserStatus | None = None
    """
    User.status[obj]: Optional, Read-only.

    Stateful status information about the User.
    """
