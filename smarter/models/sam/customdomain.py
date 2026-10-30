"""
SAM model of the ``CustomDomain`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from smarter.models.sam.base import SAMModel


class SAMCustomDomainMetadata(SAMModel):
    """Smarter API CustomDomain Manifest - Metadata class."""

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
