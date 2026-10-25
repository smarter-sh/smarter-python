"""
LLMHosts: open-weight models that the platform serves on its own Kubernetes cluster.

.. code-block:: python

    models = client.llm_hosts.discover(query="qwen", task="chat")
    plan = client.llm_hosts.plan(3)          # what deploying would create, without creating it
    status = client.llm_hosts.status(3)
"""

from __future__ import annotations

from smarter.core.typing import SmarterIdType
from smarter.models.llmhost import (
    DiscoveredManifest,
    DiscoveredModel,
    DiscoveredModels,
    LLMHost,
    LLMHostLogs,
    LLMHostPlan,
    LLMHostReport,
    LLMHostStatus,
)
from smarter.models.manifest import Manifest

from .base import SmarterKindResource, resource_id


class LLMHosts(SmarterKindResource[LLMHost]):
    """LLMHosts: ``/api/v1/llmhosts/``, and the manifest api's ``LLMHost`` kind."""

    kind = "LLMHost"
    path = "llmhosts/"
    model = LLMHost

    def status(self, id: SmarterIdType) -> LLMHostStatus:  # pylint: disable=redefined-builtin
        """
        An LLMHost's state, read from Kubernetes now.

        :param id: The LLMHost's id or hashed id.
        :returns: Its status, replicas and pods.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/status/", cast_to=LLMHostStatus)

    def logs(self, id: SmarterIdType, *, tail: int = 200) -> LLMHostLogs:  # pylint: disable=redefined-builtin
        """
        The latest log lines of an LLMHost's pods.

        :param id: The LLMHost's id or hashed id.
        :param tail: How many lines.
        :returns: The logs.
        """
        return self._http.request(
            "GET", f"{self.path}{resource_id(id)}/logs/", params={"tail": tail}, cast_to=LLMHostLogs
        )

    def plan(self, id: SmarterIdType) -> LLMHostPlan:  # pylint: disable=redefined-builtin
        """
        The Kubernetes resources that deploying an LLMHost would create, without creating them.

        :param id: The LLMHost's id or hashed id.
        :returns: The resources.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/plan/", cast_to=LLMHostPlan)

    def deploy(self, id: SmarterIdType) -> LLMHostStatus:  # pylint: disable=redefined-builtin
        """
        Deploy an LLMHost on the platform's cluster.

        This creates real, billable infrastructure, e.g. GPU nodes. Check :meth:`plan` first.

        :param id: The LLMHost's id or hashed id.
        :returns: Its state.
        """
        return self._http.request("POST", f"{self.path}{resource_id(id)}/deploy/", cast_to=LLMHostStatus)

    def undeploy(self, id: SmarterIdType, *, purge: bool = False) -> LLMHostStatus:  # pylint: disable=redefined-builtin
        """
        Undeploy an LLMHost.

        :param id: The LLMHost's id or hashed id.
        :param purge: True to delete its model storage too.
        :returns: Its state.
        """
        return self._http.request(
            "POST",
            f"{self.path}{resource_id(id)}/undeploy/",
            params={"purge": purge or None},
            cast_to=LLMHostStatus,
        )

    def report(self) -> LLMHostReport:
        """
        A report of every LLMHost that the user may read: counts by status and engine, and estimated costs.

        :returns: The report.
        """
        return self._http.request("GET", f"{self.path}report/", cast_to=LLMHostReport)

    def discover(
        self,
        *,
        query: str | None = None,
        task: str | None = None,
        catalog: str = "huggingface",
        limit: int = 20,
    ) -> list[DiscoveredModel]:
        """
        Search a public model catalog for models that an LLMHost can serve.

        :param query: The search text, e.g. ``qwen``.
        :param task: Only models of this task, e.g. ``chat`` or ``embedding``.
        :param catalog: The catalog.
        :param limit: The maximum number of models.
        :returns: The models, each with the LLMHost manifest that would serve it.
        """
        response = self._http.request(
            "GET",
            f"{self.path}discover/",
            params={"q": query, "task": task, "catalog": catalog, "limit": limit},
            cast_to=DiscoveredModels,
        )
        return response.models

    def discover_manifest(
        self,
        repository: str,
        *,
        catalog: str = "huggingface",
        engine: str | None = None,
        name: str | None = None,
        token_secret: str | None = None,
    ) -> Manifest:
        """
        An LLMHost manifest for a model in a public catalog, ready to apply.

        :param repository: The model's repository, e.g. ``Qwen/Qwen2.5-7B-Instruct``.
        :param catalog: The catalog.
        :param engine: The inference engine, or None for the platform's choice.
        :param name: The LLMHost's name, or None for one derived from the repository.
        :param token_secret: The name of a Secret that holds the catalog's access token, for gated models.
        :returns: The manifest, which :meth:`apply` accepts.
        """
        response = self._http.request(
            "GET",
            f"{self.path}discover/manifest/",
            params={
                "repository": repository,
                "catalog": catalog,
                "engine": engine,
                "name": name,
                "tokenSecret": token_secret,
            },
            cast_to=DiscoveredManifest,
        )
        return Manifest.model_validate(response.manifest)


__all__ = ["LLMHosts"]
