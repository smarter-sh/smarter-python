"""Models of vectorstores, their documents and snapshots, and search results."""

from datetime import datetime

from pydantic import Field

from smarter.core.typing import SmarterJsonObjectType, SmarterJsonType

from .base import SmarterCamelModel, SmarterResource


class Vectorstore(SmarterResource):
    """A vectorstore: a vector database, hosted by Smarter or by a provider, for retrieval-augmented generation."""

    backend: str | None = Field(None, description="e.g. qdrant or pinecone.")
    hosting: str | None = Field(None, description="self_hosted or managed.")
    is_active: bool | None = None
    dimension: int | None = None
    metric: str | None = None
    embeddings_provider: str | None = None
    embeddings_model: str | None = None
    status: str | None = Field(None, description="e.g. pending, ready or error.")
    status_message: str | None = None
    index_name: str | None = None
    endpoint_url: str | None = None
    vector_count: int | None = None
    document_count: int | None = None
    snapshot_count: int | None = None
    spec: SmarterJsonObjectType | None = None
    deployed_at: datetime | None = None


class VectorstoreStatus(SmarterCamelModel):
    """A vectorstore's state, checked now."""

    vectorstore: str
    status: str
    message: str | None = None
    vector_count: int | None = None
    stats: SmarterJsonObjectType = {}


class VectorstoreDocument(SmarterCamelModel):
    """A document of a vectorstore: a file, a text or a url, split into chunks and embedded."""

    id: int
    name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    source: str | None = Field(None, description="upload, text or url.")
    content_type: str | None = None
    status: str | None = Field(None, description="e.g. pending, loaded, error or deleting.")
    chunk_count: int | None = None
    metadata: SmarterJsonObjectType | None = None


class VectorstoreDocuments(SmarterCamelModel):
    """A vectorstore's documents."""

    documents: list[VectorstoreDocument] = []


class VectorstoreDocumentsAdded(SmarterCamelModel):
    """
    The result of adding documents.

    Documents are loaded asynchronously, and only once the vectorstore is deployed: see ``queued``.
    """

    documents: list[VectorstoreDocument] = []
    duplicates: list[VectorstoreDocument] = Field(default_factory=list, description="Documents that already existed.")
    queued: bool = False
    message: str | None = None


class VectorstoreDocumentDeleted(SmarterCamelModel):
    """A document that is being deleted, with its chunks."""

    document: str
    status: str


class VectorstoreSearchResult(SmarterCamelModel):
    """A chunk that matched a search."""

    id: SmarterJsonType | None = None
    text: str
    metadata: SmarterJsonObjectType | None = None
    score: float | None = None


class VectorstoreSearchResults(SmarterCamelModel):
    """The chunks that matched a search, best first."""

    vectorstore: str
    results: list[VectorstoreSearchResult] = []


class VectorstoreSnapshot(SmarterCamelModel):
    """A snapshot of a vectorstore's data."""

    id: int
    name: str | None = None
    created_at: datetime | None = None
    status: str | None = None
    scheduled: bool | None = None
    size_bytes: int | None = None


class VectorstoreSnapshots(SmarterCamelModel):
    """A vectorstore's snapshots."""

    snapshots: list[VectorstoreSnapshot] = []


class VectorstoreRestored(SmarterCamelModel):
    """The result of restoring a snapshot."""

    vectorstore: str
    restored: str
    vector_count: int | None = None


__all__ = [
    "Vectorstore",
    "VectorstoreDocument",
    "VectorstoreDocumentDeleted",
    "VectorstoreDocuments",
    "VectorstoreDocumentsAdded",
    "VectorstoreRestored",
    "VectorstoreSearchResult",
    "VectorstoreSearchResults",
    "VectorstoreSnapshot",
    "VectorstoreSnapshots",
    "VectorstoreStatus",
]
