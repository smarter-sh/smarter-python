"""Models of LLMHosts: open-weight models that Smarter serves on its own Kubernetes cluster."""

from datetime import datetime

from pydantic import Field

from smarter.core.typing import SmarterJsonObjectType, SmarterJsonType

from .base import SmarterCamelModel, SmarterModel, SmarterResource


class LLMHost(SmarterResource):
    """An LLMHost: a model, the inference engine that serves it, and the compute it runs on."""

    spec: SmarterJsonObjectType | None = None
    model_source: str | None = None
    model_repository: str | None = None
    model_revision: str | None = None
    model_task: str | None = Field(None, description="e.g. chat, completion or embedding.")
    inference_engine: str | None = Field(None, description="e.g. vllm, tgi, tei, ollama or llama_cpp.")
    api_format: str | None = None
    compute: int | None = Field(None, description="The id of the LLMHostCompute that the LLMHost runs on.")
    gpu_count: int | None = None
    gpu_type: str | None = None
    replicas: int | None = None
    ready_replicas: int | None = None
    status: str | None = None
    status_message: str | None = None
    endpoint_url: str | None = None
    public_url: str | None = None
    served_model_name: str | None = None
    is_active: bool | None = None
    deployed_at: datetime | None = None
    cost_per_hour: str | None = None


class LLMHostStatus(SmarterCamelModel):
    """An LLMHost's state, read from Kubernetes now."""

    llmhost: str
    status: str
    message: str | None = None
    replicas: int | None = None
    ready_replicas: int | None = None
    healthy: bool | None = None
    endpoint: str | None = None
    public_url: str | None = None
    pods: list[SmarterJsonObjectType] = []
    checked_at: datetime | None = None


class LLMHostLogs(SmarterCamelModel):
    """The latest log lines of an LLMHost's pods."""

    llmhost: str
    logs: SmarterJsonType = None


class LLMHostPlan(SmarterCamelModel):
    """The Kubernetes resources that deploying an LLMHost would create, without creating them."""

    llmhost: str
    resources: list[SmarterJsonObjectType] = []


class LLMHostReport(SmarterCamelModel):
    """A report of every LLMHost that the user may read: counts, and estimated costs."""

    totals: SmarterJsonObjectType = {}
    by_status: dict[str, int] = {}
    by_engine: dict[str, int] = {}
    llmhosts: list[SmarterJsonObjectType] = []


class DiscoveredModel(SmarterModel):
    """A model found in a public catalog, e.g. Hugging Face, with the LLMHost manifest that would serve it."""

    catalog: str | None = None
    source: str | None = None
    repository: str
    task: str | None = None
    description: str | None = None
    license: str | None = None
    gated: bool | None = None
    downloads: int | None = None
    likes: int | None = None
    tags: list[str] = []
    manifest: SmarterJsonObjectType | None = None


class DiscoveredManifest(SmarterModel):
    """The response of ``discover/manifest/``: a drafted LLMHost manifest."""

    manifest: SmarterJsonObjectType


class DiscoveredModels(SmarterModel):
    """The models that a catalog search found."""

    models: list[DiscoveredModel] = []


__all__ = [
    "DiscoveredManifest",
    "DiscoveredModel",
    "DiscoveredModels",
    "LLMHost",
    "LLMHostLogs",
    "LLMHostPlan",
    "LLMHostReport",
    "LLMHostStatus",
]
