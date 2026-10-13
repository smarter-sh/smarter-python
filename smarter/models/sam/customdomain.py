"""
SAM model of the ``CustomDomain`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional, Union
from uuid import UUID

from pydantic import Field, constr

from smarter.models.sam.base import SAMModel


class SAMCustomDomainMetadata(SAMModel):
    """Smarter API CustomDomain Manifest - Metadata class."""

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


class SAMCustomDomainSpecConfig(SAMModel):
    """Smarter API CustomDomain Manifest - CustomDomain.spec.config."""

    domainName: str = Field(..., title="Domainname")
    """
    CustomDomain.spec.config.domainName[str].

    Required. The domain name, e.g. 'llmclients.example.com'. It cannot be changed once the domain has been registered.
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


class SAMCustomDomainSpec(SAMModel):
    """Smarter API CustomDomain Manifest - CustomDomain.spec."""

    config: SAMCustomDomainSpecConfig
    """
    CustomDomain.spec.config[object].

    Required. The configuration of the CustomDomain.
    """


class SAMCustomDomainStatus(SAMModel):
    """
    Smarter API CustomDomain Manifest - Status class.

    Read only. Besides ownership, it reports the domain's AWS Route53 hosted zone, whether
    the domain is verified, and its DNS records. The LLMClient that uses it is reported in
    ``dependencies``.
    """

    accountNumber: str = Field(..., title="Accountnumber")
    """
    CustomDomain.status.accountNumber: The account owner of this CustomDomain.

    Read only.
    """
    awsHostedZoneId: str | None = Field(None, title="Awshostedzoneid")
    """
    CustomDomain.status.awsHostedZoneId: The AWS Route53 hosted zone of this CustomDomain, once it is registered with smarter deploy.

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
    dnsRecords: list[str] | None = Field(None, title="Dnsrecords")
    """
    CustomDomain.status.dnsRecords: The DNS records of this CustomDomain.

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
    CustomDomain.status.username: The Smarter user who created this CustomDomain.

    Read only.
    """
    verificationMessage: str | None = Field(None, title="Verificationmessage")
    """
    CustomDomain.status.verificationMessage: Why the domain is not verified yet, or why its verification failed.

    Read only.
    """
    verificationStatus: str | None = Field("Not Verified", title="Verificationstatus")
    """
    CustomDomain.status.verificationStatus: Not Verified, Verifying, Verified or Failed.

    The domain is Verified when its NS records are delegated to its hosted zone, and its TLS certificate is issued. Read only.
    """
    verifiedAt: datetime | None = Field(None, title="Verifiedat")
    """
    CustomDomain.status.verifiedAt: When the domain was verified.

    Read only.
    """


class SAMCustomDomain(SAMModel):
    """Smarter API Manifest - CustomDomain."""

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
    metadata: SAMCustomDomainMetadata
    """CustomDomain.metadata[obj]: Required, the CustomDomain metadata."""
    spec: SAMCustomDomainSpec
    """CustomDomain.spec[obj]: Required, the CustomDomain specification."""
    status: SAMCustomDomainStatus | None = None
    """
    CustomDomain.status[obj]: Optional, Read-only.

    Stateful status information about the CustomDomain.
    """
