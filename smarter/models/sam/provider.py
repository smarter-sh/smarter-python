"""
SAM model of the ``Provider`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import EmailStr, Field

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


class SAMProviderMetadata(SAMModel):
    """Smarter API Provider Manifest - Metadata class."""

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


class SAMProviderSpecProvider(SAMModel):
    """Smarter API - generic API Connection class."""

    api_key: str | None = Field(None, title="Api Key")
    """The name of the Smarter Secret containing the API key to use for verification tests."""
    base_url: str | None = Field(None, title="Base Url")
    """The base URL for the Provider's API."""
    connectivity_test_path: str | None = Field("", title="Connectivity Test Path")
    """The URL path to test connectivity with the Provider's API."""
    contact_email: EmailStr | None = Field(None, title="Contact Email")
    """The contact email of the Provider."""
    description: str | None = Field(None, title="Description")
    """A brief description of the Provider."""
    docs_url: str | None = Field(None, title="Docs Url")
    """The documentation URL of the Provider."""
    logo: str | None = Field(None, title="Logo")
    """The logo of the Provider."""
    name: str = Field(..., title="Name")
    """
    The name of the Provider.

    Case sensitive. Must be unique and not empty, with no leading or trailing whitespace and no special characters. examples: 'OpenAI', 'GoogleAI', 'MetaAI'.
    """
    privacy_policy_url: str | None = Field(None, title="Privacy Policy Url")
    """The privacy policy URL of the Provider."""
    support_email: EmailStr | None = Field(None, title="Support Email")
    """The support email of the Provider."""
    terms_of_service_url: str | None = Field(None, title="Terms Of Service Url")
    """The terms of service URL of the Provider."""
    website_url: str | None = Field(None, title="Website Url")
    """The website_url URL of the Provider."""


class SAMProviderStatus(SAMModel):
    """Smarter API Provider Manifest - Status class."""

    can_activate: bool | None = Field(True, title="Can Activate")
    """
    Provider.status.can_activate: Indicates whether this Provider can be activated.

    Read only.
    """
    contact_email_verified: datetime | None = Field(None, title="Contact Email Verified")
    """
    Provider.status.contact_email_verified: The date in which the contact email for this Provider was verified.

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
    is_active: bool = Field(..., title="Is Active")
    """Provider.status.is_active: Indicates whether this Provider is currently active. Read only."""
    is_deprecated: bool = Field(..., title="Is Deprecated")
    """
    Provider.status.is_deprecated: Indicates whether this Provider is deprecated.

    Read only.
    """
    is_flagged: bool = Field(..., title="Is Flagged")
    """
    Provider.status.is_flagged: Indicates whether this Provider has been flagged for review.

    Read only.
    """
    is_suspended: bool = Field(..., title="Is Suspended")
    """
    Provider.status.is_suspended: Indicates whether this Provider is currently suspended.

    Read only.
    """
    is_verified: bool = Field(..., title="Is Verified")
    """
    Provider.status.is_verified: Indicates whether this Provider has been verified.

    Read only.
    """
    modified: datetime = Field(..., title="Modified")
    """
    The date in which this resource was most recently changed.

    Read only.
    """
    ownership_requested: EmailStr | None = Field(None, title="Ownership Requested")
    """
    Provider.status.ownership_requested: The Smarter user that has requested ownership of this Provider.

    Read only.
    """
    recordLocator: str = Field(..., title="Recordlocator")
    """
    RecordLocator[String]: An optional identifier used to locate the resource record associated with this manifest.

    Read only.
    """
    support_email_verified: datetime | None = Field(None, title="Support Email Verified")
    """
    Provider.status.support_email_verified: The date in which the support email for this Provider was verified.

    Read only.
    """
    tos_accepted_at: datetime | None = Field(None, title="Tos Accepted At")
    """
    Provider.status.tos_accepted_at: The date in which the Terms of Service for this Provider were accepted.

    Read only.
    """
    tos_accepted_by: EmailStr | None = Field(None, title="Tos Accepted By")
    """
    Provider.status.tos_accepted_by: The Smarter user that accepted the Terms of Service for this Provider.

    Read only.
    """


class SAMProviderSpec(SAMModel):
    """Smarter API Api Connection Manifest ApiConnection.spec."""

    provider: SAMProviderSpecProvider
    """Provider.spec.selector[obj]: the spec for the Provider."""


class SAMProvider(SAMModel):
    """Smarter API Manifest - Account."""

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
    metadata: SAMProviderMetadata
    """Provider.metadata[obj]: Required, the Provider metadata."""
    spec: SAMProviderSpec
    """Provider.spec[obj]: Required, the Provider specification."""
    status: SAMProviderStatus | None = None
    """
    Provider.status[obj]: Optional, Read-only.

    Stateful status information about the Provider.
    """
