"""Test smarter.resources.vectorstores."""

import tempfile
from pathlib import Path

from .base import SmarterTestBase

ADDED = {"documents": [{"id": 1, "name": "refunds", "status": "pending"}], "duplicates": [], "queued": False}


class TestVectorstores(SmarterTestBase):
    """Test Vectorstores."""

    def test_list_and_status(self):
        """Vectorstores are listed, and a vectorstore's status is checked."""
        self.route("GET", "vectorstores/", fixture="vectorstores")
        self.route("GET", "vectorstores/2/status/", fixture="vs_status")
        self.assertEqual(self.client.vectorstores.list()[0].backend, "qdrant")
        self.assertEqual(self.client.vectorstores.status(2).status, "pending")

    def test_deploy(self):
        """Deploy() and undeploy() return the vectorstore."""
        vectorstore = self.load_json("vectorstores")[0]
        self.route("POST", "vectorstores/2/deploy/", json_body=vectorstore)
        self.route("POST", "vectorstores/2/undeploy/", json_body=vectorstore)
        self.assertEqual(self.client.vectorstores.deploy(2).name, vectorstore["name"])
        self.assertEqual(self.client.vectorstores.undeploy(2).name, vectorstore["name"])

    def test_documents(self):
        """Documents are listed, added from a text, a url or files, and deleted."""
        self.route("GET", "vectorstores/2/documents/", json_body={"documents": ADDED["documents"]})
        self.route("POST", "vectorstores/2/documents/", json_body=ADDED, status=202)
        self.route("DELETE", "vectorstores/2/documents/1/", json_body={"document": "refunds", "status": "deleting"})
        self.assertEqual(self.client.vectorstores.documents(2).documents[0].name, "refunds")
        self.client.vectorstores.add_text(2, "30 days", name="refunds", metadata={"topic": "refunds"})
        self.assertEqual(self.request_json(), {"text": "30 days", "name": "refunds", "metadata": {"topic": "refunds"}})
        self.client.vectorstores.add_text(2, "30 days")
        self.assertEqual(self.request_json(), {"text": "30 days"})
        self.client.vectorstores.add_url(2, "https://example.com/faq", metadata={"a": 1})
        self.assertEqual(self.request_json(), {"url": "https://example.com/faq", "metadata": {"a": 1}})
        self.client.vectorstores.add_url(2, "https://example.com/faq")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "handbook.txt"
            path.write_text("handbook", encoding="utf-8")
            added = self.client.vectorstores.add_files(2, [path])
        self.assertFalse(added.queued)
        self.assertIn(b'filename="handbook.txt"', self.last_request.content)
        self.assertEqual(self.client.vectorstores.delete_document(2, 1).status, "deleting")

    def test_search(self):
        """Search() sends only the options that are set."""
        results = {"vectorstore": "kb", "results": [{"id": "a", "text": "30 days", "metadata": {}, "score": 0.9}]}
        self.route("POST", "vectorstores/2/search/", json_body=results)
        self.assertEqual(self.client.vectorstores.search(2, "refunds").results[0].score, 0.9)
        self.assertEqual(self.request_json(), {"query": "refunds", "k": 4, "searchType": "similarity"})
        self.client.vectorstores.search(
            2, "refunds", k=2, search_type="mmr", fetch_k=8, lambda_mult=0.5, filter={"a": 1}
        )
        self.assertEqual(
            self.request_json(),
            {"query": "refunds", "k": 2, "searchType": "mmr", "fetchK": 8, "lambdaMult": 0.5, "filter": {"a": 1}},
        )

    def test_snapshots(self):
        """Snapshots are listed, taken and restored."""
        snapshot = {"id": 3, "name": "s3", "status": "ready"}
        self.route("GET", "vectorstores/2/snapshots/", json_body={"snapshots": [snapshot]})
        self.route("POST", "vectorstores/2/snapshots/", json_body=snapshot, status=201)
        self.route(
            "POST",
            "vectorstores/2/snapshots/3/restore/",
            json_body={"vectorstore": "kb", "restored": "s3", "vectorCount": 10},
        )
        self.assertEqual(self.client.vectorstores.snapshots(2).snapshots[0].id, 3)
        self.assertEqual(self.client.vectorstores.create_snapshot(2).name, "s3")
        self.assertEqual(self.client.vectorstores.restore(2, 3).vector_count, 10)
