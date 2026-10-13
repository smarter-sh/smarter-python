"""
SAM model of the ``Secret`` kind, generated from the Smarter platform's JSON Schema.

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


class SAMSecretMetadata(SAMModel):
    """Smarter API Secret Manifest - Metadata class."""

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
    """
    Secret.metadata.name[str].

    Required. The name of the secret. camelCase, no spaces, no special characters.
    """
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


class SAMSecretSpecConfig(SAMModel):
    """Smarter API Secret Manifest Secret.spec.config."""

    expiration_date: datetime | None = Field(None, title="Expiration Date")
    """
    Secret.spec.configuration.expiration_date[str].

    Optional. The expiration date of the Secret.
    """
    value: str = Field(..., title="Value")
    """
    Secret.spec.configuration.value[str].

    Required. The unencrypted value of the Secret.
    """


class SAMSecretStatus(SAMModel):
    """Smarter API Secret Manifest - Status class (read-only, like Kubernetes status attributes)."""

    accountNumber: str = Field(..., title="Accountnumber")
    """
    Secret.status.account_number: The account owner of this Secret.

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
    last_accessed: datetime | None = Field(None, title="Last Accessed")
    """
    Secret.status.last_accessed: The date in which this Secret was most recently accessed.

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
    username: str = Field(..., title="Username")
    """
    Secret.status.account_number: The Smarter user who created this Secret.

    Read only.
    """


class SAMSecretSpec(SAMModel):
    """Smarter API Secret Manifest Secret.spec."""

    config: SAMSecretSpecConfig
    """
    Secret.spec.config[object].

    The configuration for the Secret.
    """


class SAMSecret(SAMModel):
    """Smarter API Manifest - Secret."""

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
    metadata: SAMSecretMetadata
    """Secret.metadata[obj]: Required, the Secret metadata."""
    spec: SAMSecretSpec
    """Secret.spec[obj]: Required, the Secret specification."""
    status: SAMSecretStatus | None = None
    """
    Secret.status[obj]: Optional, Read-only.

    Stateful status information about the Secret.
    """
