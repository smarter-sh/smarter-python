"""
Vectorstores: vector databases for retrieval-augmented generation.

.. code-block:: python

    client.vectorstores.add_text(2, "Our refund window is 30 days.", name="refunds")
    client.vectorstores.add_files(2, ["handbook.pdf"])
    for result in client.vectorstores.search(2, "How long is the refund window?").results:
        print(result.score, result.text)
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Literal

from smarter.core.typing import SmarterIdType, SmarterJsonObjectType, SmarterJsonType
from smarter.models.vectorstore import (
    Vectorstore,
    VectorstoreDocumentDeleted,
    VectorstoreDocuments,
    VectorstoreDocumentsAdded,
    VectorstoreRestored,
    VectorstoreSearchResults,
    VectorstoreSnapshot,
    VectorstoreSnapshots,
    VectorstoreStatus,
)

from .base import SmarterKindResource, resource_id


class Vectorstores(SmarterKindResource[Vectorstore]):
    """
    Vectorstores: ``/api/v1/vectorstores/``, and the manifest api's ``Vectorstore`` kind.

    The platform serves these endpoints only when ``SMARTER_ENABLE_VECTORSTORE`` is true.
    """

    kind = "Vectorstore"
    path = "vectorstores/"
    model = Vectorstore

    def status(self, id: SmarterIdType) -> VectorstoreStatus:  # pylint: disable=redefined-builtin
        """
        A vectorstore's state, checked now.

        :param id: The vectorstore's id or hashed id.
        :returns: Its status and vector count.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/status/", cast_to=VectorstoreStatus)

    def deploy(self, id: SmarterIdType) -> Vectorstore:  # pylint: disable=redefined-builtin
        """
        Deploy a vectorstore: create its database, or connect to the provider's.

        A self-hosted vectorstore creates real, possibly billable, Kubernetes resources.

        :param id: The vectorstore's id or hashed id.
        :returns: The vectorstore.
        """
        return self._http.request("POST", f"{self.path}{resource_id(id)}/deploy/", cast_to=Vectorstore)

    def undeploy(self, id: SmarterIdType) -> Vectorstore:  # pylint: disable=redefined-builtin
        """
        Stop serving a vectorstore.

        A self-hosted server's data is kept.

        :param id: The vectorstore's id or hashed id.
        :returns: The vectorstore.
        """
        return self._http.request("POST", f"{self.path}{resource_id(id)}/undeploy/", cast_to=Vectorstore)

    def documents(self, id: SmarterIdType) -> VectorstoreDocuments:  # pylint: disable=redefined-builtin
        """
        A vectorstore's documents, newest first.

        :param id: The vectorstore's id or hashed id.
        :returns: The documents.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/documents/", cast_to=VectorstoreDocuments)

    def add_text(
        self,
        id: SmarterIdType,  # pylint: disable=redefined-builtin
        text: str,
        *,
        name: str | None = None,
        metadata: Mapping[str, SmarterJsonType] | None = None,
    ) -> VectorstoreDocumentsAdded:
        """
        Add a text as a document.

        :param id: The vectorstore's id or hashed id.
        :param text: The text.
        :param name: The document's name.
        :param metadata: A JSON object, stored with each of the document's chunks.
        :returns: The added document. It is loaded asynchronously, once the vectorstore is deployed.
        """
        body: SmarterJsonObjectType = {"text": text}
        if name:
            body["name"] = name
        if metadata is not None:
            body["metadata"] = dict(metadata)
        return self._http.request(
            "POST", f"{self.path}{resource_id(id)}/documents/", json=body, cast_to=VectorstoreDocumentsAdded
        )

    def add_url(
        self,
        id: SmarterIdType,  # pylint: disable=redefined-builtin
        url: str,
        *,
        metadata: Mapping[str, SmarterJsonType] | None = None,
    ) -> VectorstoreDocumentsAdded:
        """
        Add a public web page or file, by its url, as a document.

        The platform fetches it.

        :param id: The vectorstore's id or hashed id.
        :param url: The url.
        :param metadata: A JSON object, stored with each of the document's chunks.
        :returns: The added document.
        """
        body: SmarterJsonObjectType = {"url": url}
        if metadata is not None:
            body["metadata"] = dict(metadata)
        return self._http.request(
            "POST", f"{self.path}{resource_id(id)}/documents/", json=body, cast_to=VectorstoreDocumentsAdded
        )

    def add_files(
        self,
        id: SmarterIdType,  # pylint: disable=redefined-builtin
        files: Sequence[str | Path],
    ) -> VectorstoreDocumentsAdded:
        """
        Upload files as documents, e.g. PDF, Word, HTML or text files.

        The platform extracts their text.

        :param id: The vectorstore's id or hashed id.
        :param files: The files' paths.
        :returns: The added documents.
        """
        handles = [open(Path(path), "rb") for path in files]  # pylint: disable=consider-using-with
        try:
            uploads = [("files", (Path(handle.name).name, handle)) for handle in handles]
            return self._http.request(
                "POST", f"{self.path}{resource_id(id)}/documents/", files=uploads, cast_to=VectorstoreDocumentsAdded
            )
        finally:
            for handle in handles:
                handle.close()

    def delete_document(
        self, id: SmarterIdType, document_id: int
    ) -> VectorstoreDocumentDeleted:  # pylint: disable=redefined-builtin
        """
        Remove a document and its chunks.

        The removal is asynchronous.

        :param id: The vectorstore's id or hashed id.
        :param document_id: The document's id.
        :returns: The document, being deleted.
        """
        return self._http.request(
            "DELETE",
            f"{self.path}{resource_id(id)}/documents/{resource_id(document_id)}/",
            cast_to=VectorstoreDocumentDeleted,
        )

    def search(
        self,
        id: SmarterIdType,  # pylint: disable=redefined-builtin
        query: str,
        *,
        k: int = 4,
        search_type: Literal["similarity", "mmr", "similarity_score_threshold"] = "similarity",
        score_threshold: float | None = None,
        fetch_k: int | None = None,
        lambda_mult: float | None = None,
        filter: Mapping[str, SmarterJsonType] | None = None,  # pylint: disable=redefined-builtin
    ) -> VectorstoreSearchResults:
        """
        Search a vectorstore.

        :param id: The vectorstore's id or hashed id.
        :param query: The search text.
        :param k: How many chunks to return. The platform caps it.
        :param search_type: ``similarity``, ``mmr`` (maximal marginal relevance), or ``similarity_score_threshold``.
        :param score_threshold: The minimum score, for ``similarity_score_threshold``.
        :param fetch_k: How many chunks ``mmr`` considers.
        :param lambda_mult: ``mmr``'s balance of relevance (1) and diversity (0).
        :param filter: Only chunks whose metadata match.
        :returns: The matching chunks, best first.
        """
        body: SmarterJsonObjectType = {"query": query, "k": k, "searchType": search_type}
        optional: dict[str, SmarterJsonType] = {
            "scoreThreshold": score_threshold,
            "fetchK": fetch_k,
            "lambdaMult": lambda_mult,
            "filter": dict(filter) if filter else None,
        }
        body.update({key: value for key, value in optional.items() if value is not None})
        return self._http.request(
            "POST", f"{self.path}{resource_id(id)}/search/", json=body, cast_to=VectorstoreSearchResults
        )

    def snapshots(self, id: SmarterIdType) -> VectorstoreSnapshots:  # pylint: disable=redefined-builtin
        """
        A vectorstore's snapshots.

        :param id: The vectorstore's id or hashed id.
        :returns: The snapshots.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/snapshots/", cast_to=VectorstoreSnapshots)

    def create_snapshot(self, id: SmarterIdType) -> VectorstoreSnapshot:  # pylint: disable=redefined-builtin
        """
        Take a snapshot of a vectorstore's data now.

        :param id: The vectorstore's id or hashed id.
        :returns: The snapshot.
        """
        return self._http.request("POST", f"{self.path}{resource_id(id)}/snapshots/", cast_to=VectorstoreSnapshot)

    def restore(self, id: SmarterIdType, snapshot_id: int) -> VectorstoreRestored:  # pylint: disable=redefined-builtin
        """
        Replace a vectorstore's data with one of its snapshots.

        :param id: The vectorstore's id or hashed id.
        :param snapshot_id: The snapshot's id.
        :returns: The restored vector count.
        """
        return self._http.request(
            "POST",
            f"{self.path}{resource_id(id)}/snapshots/{resource_id(snapshot_id)}/restore/",
            cast_to=VectorstoreRestored,
        )


__all__ = ["Vectorstores"]
