"""
SAM model of the ``Vectorstore`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Optional, Union
from uuid import UUID

from pydantic import Field, conint, constr

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


class SAMVectorstoreEmbeddings(SAMModel):
    """Vectorstore.spec.embeddings: how documents and queries are turned into vectors."""

    batchSize: conint(ge=1, le=1000) | None = Field(64, title="Batchsize")
    """Vectorstore.__init__.embeddings.batchSize: chunks per embeddings request and upsert."""
    chunkOverlap: conint(ge=0, le=2000) | None = Field(200, title="Chunkoverlap")
    """Vectorstore.__init__.embeddings.chunkOverlap: characters shared by consecutive chunks."""
    chunkSize: conint(ge=100, le=8000) | None = Field(1000, title="Chunksize")
    """Vectorstore.__init__.embeddings.chunkSize: characters per chunk."""
    dimensions: conint(ge=1, le=20000) | None = Field(None, title="Dimensions")
    """
    Vectorstore.__init__.embeddings.dimensions: ask the model for vectors of this size, if it supports it, e.g. text-embedding-3.

    It must equal index.dimension.
    """
    model: constr(min_length=1) = Field(..., title="Model")
    """Vectorstore.__init__.embeddings.model: the embeddings model, e.g. text-embedding-3-small."""
    provider: constr(min_length=1) = Field(..., title="Provider")
    """Vectorstore.__init__.embeddings.provider: a Provider with an OpenAI-compatible embeddings API, e.g. openai."""


class Metric(Enum):
    """Vectorstore.__init__.index.metric: the distance metric."""

    cosine = "cosine"
    euclidean = "euclidean"
    dotproduct = "dotproduct"


class SAMVectorstoreIndex(SAMModel):
    """Vectorstore.spec.index: the index (Pinecone), or collection (Qdrant), of the database."""

    deletionProtection: bool | None = Field(False, title="Deletionprotection")
    """Vectorstore.__init__.index.deletionProtection: refuse to destroy the database."""
    dimension: conint(ge=1, le=20000) = Field(..., title="Dimension")
    """Vectorstore.__init__.index.dimension: of the embeddings model's vectors."""
    metric: Metric | None = Field("cosine", title="Metric")
    """Vectorstore.__init__.index.metric: the distance metric."""
    name: constr(max_length=45) | None = Field(None, title="Name")
    """
    Vectorstore.__init__.index.name: the index or collection's name, in lowercase letters, digits and hyphens.

    Defaults to the manifest's name, with the account number for a managed service.
    """


class SAMVectorstoreMaintenance(SAMModel):
    """Vectorstore.spec.maintenance: what Celery Beat does, besides checking its status."""

    snapshotIntervalHours: conint(ge=1, le=720) | None = Field(24, title="Snapshotintervalhours")
    """Vectorstore.__init__.maintenance.snapshotIntervalHours: how often."""
    snapshotRetention: conint(ge=1, le=100) | None = Field(7, title="Snapshotretention")
    """
    Vectorstore.__init__.maintenance.snapshotRetention: how many are kept.

    Older ones are deleted.
    """
    snapshots: bool | None = Field(True, title="Snapshots")
    """Vectorstore.__init__.maintenance.snapshots: take Qdrant snapshots, or Pinecone backups."""


class SAMVectorstoreMetadata(SAMModel):
    """Smarter API Vectorstore Manifest - Metadata class."""

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


class Cloud(Enum):
    """Vectorstore.__init__.pinecone.cloud."""

    aws = "aws"
    gcp = "gcp"
    azure = "azure"


class SAMVectorstorePinecone(SAMModel):
    """Vectorstore.spec.pinecone: where Pinecone runs a serverless index."""

    cloud: Cloud | None = Field("aws", title="Cloud")
    """Vectorstore.__init__.pinecone.cloud."""
    region: constr(min_length=1) | None = Field("us-east-1", title="Region")
    """Vectorstore.__init__.pinecone.region."""


class SAMVectorstoreSelfHosted(SAMModel):
    """Vectorstore.spec.selfHosted: the Qdrant server that Smarter runs on Kubernetes."""

    cpu: str | None = Field("500m", title="Cpu")
    """Vectorstore.__init__.selfHosted.cpu: requested, e.g. 500m."""
    image: str | None = Field("qdrant/qdrant:v1.19.1", title="Image")
    """Vectorstore.__init__.selfHosted.image: the Qdrant image."""
    memory: str | None = Field("1Gi", title="Memory")
    """Vectorstore.__init__.selfHosted.memory: requested, e.g. 1Gi."""
    storage: str | None = Field("10Gi", title="Storage")
    """Vectorstore.__init__.selfHosted.storage: the size of its volume, e.g. 10Gi."""
    storageClass: str | None = Field(None, title="Storageclass")
    """
    Vectorstore.__init__.selfHosted.storageClass: of its volume.

    Defaults to the cluster's.
    """


class Backend(Enum):
    """Vectorstore.__init__.backend: qdrant or pinecone."""

    qdrant = "qdrant"
    pinecone = "pinecone"


class Hosting(Enum):
    """Vectorstore.__init__.hosting: self_hosted, run by Smarter on Kubernetes (qdrant only), or managed, a service reached through the ApiConnection in connection."""

    self_hosted = "self_hosted"
    managed = "managed"


class SAMVectorstoreSpec(SAMModel):
    """Smarter API Vectorstore Manifest Vectorstore.spec."""

    backend: Backend = Field(..., title="Backend")
    """Vectorstore.__init__.backend: qdrant or pinecone."""
    connection: str | None = Field(None, title="Connection")
    """
    Vectorstore.__init__.connection: managed only.

    The name of an ApiConnection with the service's URL and API key Secret, e.g. https://api.pinecone.io, or a Qdrant Cloud cluster's URL.
    """
    embeddings: SAMVectorstoreEmbeddings
    """Vectorstore.__init__.embeddings."""
    hosting: Hosting | None = Field("managed", title="Hosting")
    """Vectorstore.__init__.hosting: self_hosted, run by Smarter on Kubernetes (qdrant only), or managed, a service reached through the ApiConnection in connection."""
    index: SAMVectorstoreIndex
    """Vectorstore.__init__.index."""
    isActive: bool | None = Field(True, title="Isactive")
    """Vectorstore.__init__.isActive: whether it may be used."""
    maintenance: SAMVectorstoreMaintenance | None = None
    """Vectorstore.__init__.maintenance."""
    pinecone: SAMVectorstorePinecone | None = None
    """Vectorstore.__init__.pinecone: pinecone only."""
    selfHosted: SAMVectorstoreSelfHosted | None = None
    """Vectorstore.__init__.selfHosted: self_hosted only."""


class SAMVectorstoreStatus(SAMModel):
    """
    Smarter API Vectorstore Manifest - Status class.

    Read only.
    """

    accountNumber: str = Field(..., title="Accountnumber")
    """
    Vectorstore.status.accountNumber: the owner's account.

    Read only.
    """
    apiKeySecret: str | None = Field(None, title="Apikeysecret")
    """Vectorstore.status.apiKeySecret: the Secret with a self-hosted database's API key."""
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
    deployedAt: datetime | None = Field(None, title="Deployedat")
    documentCount: int | None = Field(0, title="Documentcount")
    """Vectorstore.status.documentCount: its documents."""
    endpoint: str | None = Field(None, title="Endpoint")
    """Vectorstore.status.endpoint: where it is reached."""
    indexName: str | None = Field(None, title="Indexname")
    """Vectorstore.status.indexName: the Pinecone index, or Qdrant collection."""
    lastCheckedAt: datetime | None = Field(None, title="Lastcheckedat")
    lastMaintenanceAt: datetime | None = Field(None, title="Lastmaintenanceat")
    lastSnapshotAt: datetime | None = Field(None, title="Lastsnapshotat")
    message: str | None = Field(None, title="Message")
    """Vectorstore.status.message: why, if it failed."""
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
    snapshotCount: int | None = Field(0, title="Snapshotcount")
    """Vectorstore.status.snapshotCount: its snapshots, or backups."""
    username: str = Field(..., title="Username")
    """
    Vectorstore.status.username: the owner.

    Read only.
    """
    vectorCount: int | None = Field(0, title="Vectorcount")
    """Vectorstore.status.vectorCount: as of lastCheckedAt."""
    vectorstoreStatus: str = Field(..., title="Vectorstorestatus")
    """Vectorstore.status.vectorstoreStatus: pending, provisioning, ready, stopped, failed or deleting."""


class SAMVectorstore(SAMModel):
    """Smarter API Manifest - Vectorstore."""

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
    metadata: SAMVectorstoreMetadata
    """Vectorstore.metadata[obj]: Required, the Vectorstore metadata."""
    spec: SAMVectorstoreSpec
    """Vectorstore.spec[obj]: Required, the Vectorstore specification."""
    status: SAMVectorstoreStatus | None = None
    """
    Vectorstore.status[obj]: Optional, Read-only.

    Stateful status information about the Vectorstore.
    """
