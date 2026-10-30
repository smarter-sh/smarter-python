"""
SAM model of the ``Account`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from smarter.models.sam.base import SAMModel


class SAMAccountMetadata(SAMModel):
    """Smarter API Account Manifest - Metadata class."""

    accountNumber: str | None = Field(None, title="Accountnumber")
    """
    Account.metadata.accountNumber[str].

    Your preassigned 12-digit account number for your Smarter Account in the format '####-####-####'. Read only.
    """
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


class SAMAccountSpecConfig(SAMModel):
    """Smarter API Account Manifest Account.spec.config."""

    address1: str | None = Field(None, title="Address1")
    """
    Account.spec.configuration.address1[str].

    The primary address for the Account.
    """
    address2: str | None = Field(None, title="Address2")
    """
    Account.spec.configuration.address2[str].

    Optional. The secondary address for the Account.
    """
    city: str | None = Field(None, title="City")
    """
    Account.spec.configuration.city[str].

    The city for the Account.
    """
    companyName: str = Field(..., title="Companyname")
    """
    Account.spec.configuration.companyName[str].

    The legal entity of your Smarter Account for invoicing and legal correspondence.
    """
    country: str | None = Field("US", title="Country")
    """
    Account.spec.configuration.country[str].

    The ISO 3166 country code for the Account. Default: USA.
    """
    currency: str | None = Field("USD", title="Currency")
    """
    Account.spec.configuration.currency[str].

    The primary ISO 4217 currency for the Account. Default: USD.
    """
    language: str | None = Field("en-US", title="Language")
    """
    Account.spec.configuration.language[str].

    The primary BCP 47 language tag for the Account. Default: en-US.
    """
    phoneNumber: str | None = Field(None, title="Phonenumber")
    """
    Account.spec.configuration.phoneNumber[str].

    The primary phone number for the Account.
    """
    postalCode: str | None = Field(None, title="Postalcode")
    """
    Account.spec.configuration.postalCode[str].

    The postal code for the Account.
    """
    state: str | None = Field(None, title="State")
    """
    Account.spec.configuration.state[str].

    The state for the Account.
    """
    timezone: str | None = Field("America/New_York", title="Timezone")
    """
    Account.spec.configuration.timezone[str].

    The primary IANA timezone for the Account. Default: America/New_York.
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


class SAMAccountSpec(SAMModel):
    """Smarter API Account Manifest Account.spec."""

    config: SAMAccountSpecConfig
    """
    Account.spec.config[object].

    The configuration for the Account.
    """


class SAMAccountStatus(SAMModel):
    """Smarter API Account Manifest - Status class."""

    adminAccount: str = Field(..., title="Adminaccount")
    """
    Account.status.adminAccount: The designated Smarter admin user for this Account.

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


class SAMAccount(SAMModel):
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
    metadata: SAMAccountMetadata
    """Account.metadata[obj]: Required, the Account metadata."""
    spec: SAMAccountSpec
    """Account.spec[obj]: Required, the Account specification."""
    status: SAMAccountStatus | None = None
    """
    Account.status[obj]: Optional, Read-only.

    Stateful status information about the Account.
    """
