"""Models of LLMHosts: open-weight models that Smarter serves on its own Kubernetes cluster."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from smarter.core.typing import SmarterJsonObjectType, SmarterJsonType

from .base import SmarterCamelModel, SmarterModel, SmarterResource


class LLMHost(SmarterResource):
    """An LLMHost: a model, the inference engine that serves it, and the compute it runs on."""

    spec: Optional[SmarterJsonObjectType] = None
    model_source: Optional[str] = None
    model_repository: Optional[str] = None
    model_revision: Optional[str] = None
    model_task: Optional[str] = Field(None, description="e.g. chat, completion or embedding.")
    inference_engine: Optional[str] = Field(None, description="e.g. vllm, tgi, tei, ollama or llama_cpp.")
    api_format: Optional[str] = None
    compute: Optional[int] = Field(None, description="The id of the LLMHostCompute that the LLMHost runs on.")
    gpu_count: Optional[int] = None
    gpu_type: Optional[str] = None
    replicas: Optional[int] = None
    ready_replicas: Optional[int] = None
    status: Optional[str] = None
    status_message: Optional[str] = None
    endpoint_url: Optional[str] = None
    public_url: Optional[str] = None
    served_model_name: Optional[str] = None
    is_active: Optional[bool] = None
    deployed_at: Optional[datetime] = None
    cost_per_hour: Optional[str] = None


class LLMHostStatus(SmarterCamelModel):
    """An LLMHost's state, read from Kubernetes now."""

    llmhost: str
    status: str
    message: Optional[str] = None
    replicas: Optional[int] = None
    ready_replicas: Optional[int] = None
    healthy: Optional[bool] = None
    endpoint: Optional[str] = None
    public_url: Optional[str] = None
    pods: list[SmarterJsonObjectType] = []
    checked_at: Optional[datetime] = None


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

    catalog: Optional[str] = None
    source: Optional[str] = None
    repository: str
    task: Optional[str] = None
    description: Optional[str] = None
    license: Optional[str] = None
    gated: Optional[bool] = None
    downloads: Optional[int] = None
    likes: Optional[int] = None
    tags: list[str] = []
    manifest: Optional[SmarterJsonObjectType] = None


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
