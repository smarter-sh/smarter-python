"""Models of vectorstores, their documents and snapshots, and search results."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from smarter.core.typing import SmarterJsonObjectType, SmarterJsonType

from .base import SmarterCamelModel, SmarterResource


class Vectorstore(SmarterResource):
    """A vectorstore: a vector database, hosted by Smarter or by a provider, for retrieval-augmented generation."""

    backend: Optional[str] = Field(None, description="e.g. qdrant or pinecone.")
    hosting: Optional[str] = Field(None, description="self_hosted or managed.")
    is_active: Optional[bool] = None
    dimension: Optional[int] = None
    metric: Optional[str] = None
    embeddings_provider: Optional[str] = None
    embeddings_model: Optional[str] = None
    status: Optional[str] = Field(None, description="e.g. pending, ready or error.")
    status_message: Optional[str] = None
    index_name: Optional[str] = None
    endpoint_url: Optional[str] = None
    vector_count: Optional[int] = None
    document_count: Optional[int] = None
    snapshot_count: Optional[int] = None
    spec: Optional[SmarterJsonObjectType] = None
    deployed_at: Optional[datetime] = None


class VectorstoreStatus(SmarterCamelModel):
    """A vectorstore's state, checked now."""

    vectorstore: str
    status: str
    message: Optional[str] = None
    vector_count: Optional[int] = None
    stats: SmarterJsonObjectType = {}


class VectorstoreDocument(SmarterCamelModel):
    """A document of a vectorstore: a file, a text or a url, split into chunks and embedded."""

    id: int
    name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    source: Optional[str] = Field(None, description="upload, text or url.")
    content_type: Optional[str] = None
    status: Optional[str] = Field(None, description="e.g. pending, loaded, error or deleting.")
    chunk_count: Optional[int] = None
    metadata: Optional[SmarterJsonObjectType] = None


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
    message: Optional[str] = None


class VectorstoreDocumentDeleted(SmarterCamelModel):
    """A document that is being deleted, with its chunks."""

    document: str
    status: str


class VectorstoreSearchResult(SmarterCamelModel):
    """A chunk that matched a search."""

    id: Optional[SmarterJsonType] = None
    text: str
    metadata: Optional[SmarterJsonObjectType] = None
    score: Optional[float] = None


class VectorstoreSearchResults(SmarterCamelModel):
    """The chunks that matched a search, best first."""

    vectorstore: str
    results: list[VectorstoreSearchResult] = []


class VectorstoreSnapshot(SmarterCamelModel):
    """A snapshot of a vectorstore's data."""

    id: int
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    status: Optional[str] = None
    scheduled: Optional[bool] = None
    size_bytes: Optional[int] = None


class VectorstoreSnapshots(SmarterCamelModel):
    """A vectorstore's snapshots."""

    snapshots: list[VectorstoreSnapshot] = []


class VectorstoreRestored(SmarterCamelModel):
    """The result of restoring a snapshot."""

    vectorstore: str
    restored: str
    vector_count: Optional[int] = None


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
