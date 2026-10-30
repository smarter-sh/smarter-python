"""
SAM model of the ``Vectorsearch`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field, PositiveInt, confloat

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


class SAMVectorsearchMetadata(SAMModel):
    """Smarter API Vectorsearch Manifest - Metadata class."""

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


class SAMVectorsearchStatus(SAMModel):
    """Smarter API Vectorsearch Manifest - Status class."""

    accountNumber: str = Field(..., title="Accountnumber")
    """
    Vectorsearch.status.account_number: The account owner of this Vectorsearch.

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
    Vectorsearch.status.username: The Smarter user who created this Vectorsearch.

    Read only.
    """


class VectorsearchSearchType(Enum):
    """Supported retrieval strategies for a Vectorsearch query."""

    similarity = "similarity"
    similarity_score_threshold = "similarity_score_threshold"
    mmr = "mmr"


class SAMVectorsearchSpecConfig(SAMModel):
    """Smarter API Vectorsearch Manifest Vectorsearch.spec.config."""

    auth_secret_name: str | None = Field(None, title="Auth Secret Name")
    """Optional name of the Secret used to authenticate against the Vectorstore, if required."""
    fetch_k: PositiveInt | None = Field(None, title="Fetch K")
    """
    Number of candidate documents to fetch before MMR re-ranking.

    Only valid when search_type='mmr'.
    """
    is_enabled: bool | None = Field(True, title="Is Enabled")
    """Whether this Vectorsearch is active and eligible to be queried."""
    k: PositiveInt | None = Field(4, title="K")
    """Number of top results to return from the search."""
    lambda_mult: confloat(ge=0.0, le=1.0) | None = Field(None, title="Lambda Mult")
    """
    Diversity vs.

    relevance trade-off for MMR (0.0=max diversity, 1.0=max relevance). Only valid when search_type='mmr'.
    """
    metadata_filter: dict[str, Any] | None = Field(None, title="Metadata Filter")
    """Optional metadata filter applied to the Vectorstore query, e.g. {'source': 'faq'}."""
    score_threshold: confloat(ge=0.0, le=1.0) | None = Field(None, title="Score Threshold")
    """
    Minimum relevance score a result must meet to be included.

    Only valid when search_type='similarity_score_threshold'.
    """
    search_type: VectorsearchSearchType | None = "similarity"
    """The retrieval strategy to use when querying the Vectorstore."""
    vectorstore_name: str = Field(..., title="Vectorstore Name")
    """The name of the locally-hosted Vectorstore this search queries against."""


class SAMVectorsearchSpec(SAMModel):
    """Smarter API Vectorsearch Manifest Vectorsearch.spec."""

    config: SAMVectorsearchSpecConfig
    """
    Vectorsearch.spec.config[object].

    The configuration for the Vectorsearch.
    """


class SAMVectorsearch(SAMModel):
    """Smarter API Manifest - Vectorsearch."""

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
    metadata: SAMVectorsearchMetadata
    """Vectorsearch.metadata[obj]: Required, the Vectorsearch metadata."""
    spec: SAMVectorsearchSpec
    """Vectorsearch.spec[obj]: Required, the Vectorsearch specification."""
    status: SAMVectorsearchStatus | None = None
    """
    Vectorsearch.status[obj]: Optional, Read-only.

    Stateful status information about the Vectorsearch.
    """
