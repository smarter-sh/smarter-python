"""Test smarter.resources.llmhosts."""

from .base import SmarterTestBase


class TestLLMHosts(SmarterTestBase):
    """Test LLMHosts."""

    def test_read(self):
        """LLMHosts are listed, and their status, logs, plan and report are read."""
        self.route("GET", "llmhosts/", fixture="llmhosts")
        self.route("GET", "llmhosts/1/status/", fixture="llmhost_status")
        self.route("GET", "llmhosts/1/logs/", json_body={"llmhost": "m", "logs": "line"})
        self.route("GET", "llmhosts/1/plan/", fixture="llmhost_plan")
        self.route("GET", "llmhosts/report/", fixture="llmhost_report")
        self.assertEqual(self.client.llm_hosts.list()[0].inference_engine, "tei")
        self.assertEqual(self.client.llm_hosts.status(1).status, "inactive")
        self.assertEqual(self.client.llm_hosts.logs(1, tail=5).logs, "line")
        self.assertEqual(self.last_request.url.params["tail"], "5")
        self.assertEqual(self.client.llm_hosts.plan(1).resources[0]["kind"], "PersistentVolumeClaim")
        self.assertEqual(self.client.llm_hosts.report().totals["llmhosts"], 24)

    def test_deploy(self):
        """Deploy() and undeploy() return the state, and undeploy purges only when told to."""
        state = {"llmhost": "m", "status": "pending"}
        self.route("POST", "llmhosts/1/deploy/", json_body=state, status=202)
        self.route("POST", "llmhosts/1/undeploy/", json_body=state)
        self.assertEqual(self.client.llm_hosts.deploy(1).status, "pending")
        self.client.llm_hosts.undeploy(1)
        self.assertNotIn("purge", self.last_request.url.params)
        self.client.llm_hosts.undeploy(1, purge=True)
        self.assertEqual(self.last_request.url.params["purge"], "true")

    def test_discover(self):
        """``discover()`` searches a catalog, and ``discover_manifest()`` drafts a manifest."""
        self.route("GET", "llmhosts/discover/", fixture="llmhost_discover")
        models = self.client.llm_hosts.discover(query="minilm", limit=2)
        self.assertEqual(models[0].repository, "sentence-transformers/all-MiniLM-L6-v2")
        self.assertEqual(dict(self.last_request.url.params), {"q": "minilm", "catalog": "huggingface", "limit": "2"})
        manifest = self.load_json("sam/LLMHost.example")
        self.route("GET", "llmhosts/discover/manifest/", json_body={"manifest": manifest})
        drafted = self.client.llm_hosts.discover_manifest("sentence-transformers/all-MiniLM-L6-v2", engine="tei")
        self.assertEqual(drafted.kind, "LLMHost")
        self.assertEqual(self.last_request.url.params["engine"], "tei")
