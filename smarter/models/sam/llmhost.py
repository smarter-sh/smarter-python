"""
SAM model of the ``LLMHost`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Optional, Union
from uuid import UUID

from pydantic import ConfigDict, Field, confloat, conint

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


class ApiFormat(Enum):
    """
    LLMHost.spec.engine.apiFormat[str]: the wire protocol.

    One of: ['openai_compatible', 'huggingface', 'ollama_native', 'custom'].
    """

    openai_compatible = "openai_compatible"
    huggingface = "huggingface"
    ollama_native = "ollama_native"
    custom = "custom"


class Name(Enum):
    """
    LLMHost.spec.engine.name[str]: the inference server.

    One of: ['vllm', 'tgi', 'sglang', 'llama_cpp', 'ollama', 'tei', 'custom'].
    """

    vllm = "vllm"
    tgi = "tgi"
    sglang = "sglang"
    llama_cpp = "llama_cpp"
    ollama = "ollama"
    tei = "tei"
    custom = "custom"


class SAMLLMHostEngineConfig(SAMModel):
    """
    Spec.engine: the inference server.

    The common settings, e.g. ``contextLength``, are translated into each engine's own
    arguments, e.g. vLLM's ``--max-model-len`` and llama.cpp's ``--ctx-size``. ``args`` and
    ``env`` are passed to the engine as they are, for everything else.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    apiFormat: ApiFormat | None = Field("openai_compatible", title="Apiformat")
    """
    LLMHost.spec.engine.apiFormat[str]: the wire protocol.

    One of: ['openai_compatible', 'huggingface', 'ollama_native', 'custom'].
    """
    args: list[str] | None = Field(None, title="Args")
    """LLMHost.spec.engine.args[list]: additional arguments, passed to the engine as they are."""
    command: list[str] | None = Field(None, title="Command")
    """
    LLMHost.spec.engine.command[list]: overrides the image's entrypoint.

    For custom engines.
    """
    contextLength: conint(ge=1) | None = Field(None, title="Contextlength")
    """LLMHost.spec.engine.contextLength[int]: the maximum context the server allocates, in tokens."""
    dtype: str | None = Field(None, title="Dtype")
    """LLMHost.spec.engine.dtype[str]: e.g. auto, bfloat16, float16."""
    env: dict[str, str] | None = Field(None, title="Env")
    """LLMHost.spec.engine.env[dict]: additional environment variables."""
    gpuMemoryUtilization: confloat(le=1.0, gt=0.0) | None = Field(None, title="Gpumemoryutilization")
    """LLMHost.spec.engine.gpuMemoryUtilization[float]: the fraction of GPU memory the server may use."""
    image: str | None = Field(None, title="Image")
    """
    LLMHost.spec.engine.image[str]: the container image.

    Defaults to the engine's official image. Pin a version in production. Required for custom.
    """
    maxConcurrentRequests: conint(ge=1) | None = Field(None, title="Maxconcurrentrequests")
    """LLMHost.spec.engine.maxConcurrentRequests[int]: the requests that one replica serves at once."""
    name: Name = Field(..., title="Name")
    """
    LLMHost.spec.engine.name[str]: the inference server.

    One of: ['vllm', 'tgi', 'sglang', 'llama_cpp', 'ollama', 'tei', 'custom'].
    """
    port: conint(ge=1, le=65535) | None = Field(None, title="Port")
    """
    LLMHost.spec.engine.port[int]: the container port.

    Defaults to the engine's port. Required for custom.
    """
    tensorParallelSize: conint(ge=1, le=16) | None = Field(None, title="Tensorparallelsize")
    """LLMHost.spec.engine.tensorParallelSize[int]: the GPUs that one replica shards the model across."""
    trustRemoteCode: bool | None = Field(False, title="Trustremotecode")
    """
    LLMHost.spec.engine.trustRemoteCode[bool]: run Python code from the model repository.

    Only for repositories that you trust.
    """


class SAMLLMHostHealthCheck(SAMModel):
    """Spec.healthCheck: the probes that decide when a replica is ready."""

    model_config = ConfigDict(
        extra="forbid",
    )
    path: str | None = Field(None, title="Path")
    """
    LLMHost.spec.healthCheck.path[str]: the HTTP health path.

    Defaults to the engine's, e.g. /health.
    """
    periodSeconds: conint(ge=1, le=300) | None = Field(10, title="Periodseconds")
    """LLMHost.spec.healthCheck.periodSeconds[int]: how often the probes run."""
    startupTimeoutSeconds: conint(ge=60, le=21600) | None = Field(3600, title="Startuptimeoutseconds")
    """
    LLMHost.spec.healthCheck.startupTimeoutSeconds[int]: the time the server has to download and load the weights before it is restarted.

    Large models need more.
    """


class SAMLLMHostMetadata(SAMModel):
    """Smarter API LLMHost Manifest - Metadata class."""

    annotations: None | (
        list[dict[str, str | int | float | bool | date | datetime | UUID | bytes | list | dict[str, Any]]]
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


class Quantization(Enum):
    """
    LLMHost.spec.model.quantization[str]: the weights' precision.

    One of: ['none', 'fp32', 'fp16', 'bf16', 'fp8', 'mxfp4', 'int8', 'int4', 'gguf', 'awq', 'gptq'].
    """

    none = "none"
    fp32 = "fp32"
    fp16 = "fp16"
    bf16 = "bf16"
    fp8 = "fp8"
    mxfp4 = "mxfp4"
    int8 = "int8"
    int4 = "int4"
    gguf = "gguf"
    awq = "awq"
    gptq = "gptq"


class Source(Enum):
    """
    LLMHost.spec.model.source[str]: where the weights come from.

    One of: ['huggingface', 'ollama', 's3', 'url', 'pvc'].
    """

    huggingface = "huggingface"
    ollama = "ollama"
    s3 = "s3"
    url = "url"
    pvc = "pvc"


class Task(Enum):
    """
    LLMHost.spec.model.task[str]: what the model does.

    One of: ['text-generation', 'embedding'].
    """

    text_generation = "text-generation"
    embedding = "embedding"


class SAMLLMHostModelCapabilities(SAMModel):
    """
    What the model can do.

    Informational, for discovery and for the LLMClients that use it.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    functionCalling: bool | None = Field(False, title="Functioncalling")
    """
    LLMHost.spec.model.capabilities.functionCalling[bool]: supports tool calls.

    Some engines also require args, e.g. vLLM's --enable-auto-tool-choice and --tool-call-parser.
    """
    reasoning: bool | None = Field(False, title="Reasoning")
    """LLMHost.spec.model.capabilities.reasoning[bool]: a reasoning model."""
    streaming: bool | None = Field(True, title="Streaming")
    """LLMHost.spec.model.capabilities.streaming[bool]: streams responses."""
    vision: bool | None = Field(False, title="Vision")
    """LLMHost.spec.model.capabilities.vision[bool]: accepts images."""


class SAMLLMHostNetwork(SAMModel):
    """
    Spec.network: how the LLMHost is reached.

    It is always reachable inside the cluster, at its Service. With ``ingress``, it is also
    reachable at ``https://<hostname>``, with a TLS certificate from cert-manager. A public
    endpoint requires an API key, unless ``allowUnauthenticated``.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    allowUnauthenticated: bool | None = Field(False, title="Allowunauthenticated")
    """
    LLMHost.spec.network.allowUnauthenticated[bool]: permit an Ingress for an engine that does not authenticate requests, e.g. tgi and ollama.

    Anyone who knows the hostname can use the model.
    """
    apiKeySecret: str | None = Field(None, title="Apikeysecret")
    """
    LLMHost.spec.network.apiKeySecret[str]: the name of a Smarter Secret with the API key that clients must send as a Bearer token.

    If omitted, Smarter generates one when the LLMHost is launched, and stores it in the Secret llmhost_<name>_api_key.
    """
    hostname: str | None = Field(None, title="Hostname")
    """
    LLMHost.spec.network.hostname[str]: the Ingress hostname.

    Defaults to <name>.llmhost.<account number>.<environment API domain>.
    """
    ingress: bool | None = Field(False, title="Ingress")
    """LLMHost.spec.network.ingress[bool]: create an Ingress."""


class SAMLLMHostResources(SAMModel):
    """
    Spec.resources: the compute that each replica, one pod, requests.

    These are the pod's resource requests, not a node's capacity. They must fit a node of the
    LLMHost's compute, which also determines the GPU model.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    cpu: str | None = Field(None, title="Cpu")
    """LLMHost.spec.resources.cpu[str]: the pod's CPU request, e.g. 4 or 3500m."""
    gpuCount: conint(ge=0, le=16) | None = Field(0, title="Gpucount")
    """
    LLMHost.spec.resources.gpuCount[int]: the GPUs per replica.

    0 runs on CPU.
    """
    gpuResource: str | None = Field("nvidia.com/gpu", title="Gpuresource")
    """LLMHost.spec.resources.gpuResource[str]: the Kubernetes extended resource, e.g. nvidia.com/gpu."""
    memory: str | None = Field(None, title="Memory")
    """LLMHost.spec.resources.memory[str]: the pod's memory request and limit, e.g. 24Gi."""
    nodeSelector: dict[str, str] | None = Field(None, title="Nodeselector")
    """LLMHost.spec.resources.nodeSelector[dict]: additional node labels."""
    serviceAccountName: str | None = Field(None, title="Serviceaccountname")
    """LLMHost.spec.resources.serviceAccountName[str]: e.g. for IRSA access to an S3 model source."""
    shmSize: str | None = Field("8Gi", title="Shmsize")
    """LLMHost.spec.resources.shmSize[str]: the size of /dev/shm."""
    tolerations: list[dict[str, Any]] | None = Field(None, title="Tolerations")
    """
    LLMHost.spec.resources.tolerations[list]: Kubernetes tolerations.

    When gpuCount > 0, a toleration of the gpuResource taint is added.
    """
    vramRequiredGb: conint(ge=0) | None = Field(None, title="Vramrequiredgb")
    """
    LLMHost.spec.resources.vramRequiredGb[int]: the GPU memory the model requires.

    Informational.
    """


class SAMLLMHostScaling(SAMModel):
    """Spec.scaling: the replicas."""

    model_config = ConfigDict(
        extra="forbid",
    )
    replicas: conint(ge=1, le=16) | None = Field(1, title="Replicas")
    """
    LLMHost.spec.scaling.replicas[int]: the replicas.

    More than one requires storage.accessMode ReadWriteMany or ReadOnlyMany.
    """


class SAMLLMHostStatus(SAMModel):
    """
    Smarter API LLMHost Manifest - Status class.

    Read only. Besides ownership, it reports the LLMHost's lifecycle state, where it can be
    reached, and its accumulated cost, as of its most recent status check.
    """

    accountNumber: str = Field(..., title="Accountnumber")
    """
    LLMHost.status.account_number: The account owner of this LLMHost.

    Read only.
    """
    apiKeySecret: str | None = Field(None, title="Apikeysecret")
    """
    LLMHost.status.apiKeySecret: the Smarter Secret with the API key, if any.

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
    deployedAt: datetime | None = Field(None, title="Deployedat")
    """
    LLMHost.status.deployedAt: when it was last launched.

    Read only.
    """
    endpoint: str | None = Field(None, title="Endpoint")
    """
    LLMHost.status.endpoint: the base URL inside the cluster, e.g. for LLMClients.

    Read only.
    """
    estimatedCost: float | str | None = Field(None, title="Estimatedcost")
    """LLMHost.status.estimatedCost: uptimeHours times replicas times each replica's share of its compute's node price. Read only."""
    healthy: bool | None = Field(None, title="Healthy")
    """
    LLMHost.status.healthy: the result of the last health check.

    Read only.
    """
    hostStatus: str | None = Field(None, title="Hoststatus")
    """
    LLMHost.status.hostStatus: the lifecycle state, e.g. pending, active or error.

    Read only.
    """
    lastCheckedAt: datetime | None = Field(None, title="Lastcheckedat")
    """
    LLMHost.status.lastCheckedAt: when its status was last checked.

    Read only.
    """
    message: str | None = Field(None, title="Message")
    """
    LLMHost.status.message: why the LLMHost is in its state, e.g. a container error.

    Read only.
    """
    modified: datetime = Field(..., title="Modified")
    """
    The date in which this resource was most recently changed.

    Read only.
    """
    publicUrl: str | None = Field(None, title="Publicurl")
    """
    LLMHost.status.publicUrl: the base URL of the Ingress, if any.

    Read only.
    """
    readyReplicas: int | None = Field(None, title="Readyreplicas")
    """
    LLMHost.status.readyReplicas: ready.

    Read only.
    """
    recordLocator: str = Field(..., title="Recordlocator")
    """
    RecordLocator[String]: An optional identifier used to locate the resource record associated with this manifest.

    Read only.
    """
    replicas: int | None = Field(None, title="Replicas")
    """
    LLMHost.status.replicas: desired.

    Read only.
    """
    uptimeHours: float | None = Field(None, title="Uptimehours")
    """
    LLMHost.status.uptimeHours: hours since deployedAt.

    Read only.
    """
    username: str = Field(..., title="Username")
    """
    LLMHost.status.username: The Smarter user who created this LLMHost.

    Read only.
    """


class AccessMode(Enum):
    """LLMHost.spec.storage.accessMode[str]: One of: ['ReadWriteOnce', 'ReadWriteMany', 'ReadOnlyMany']."""

    ReadWriteOnce = "ReadWriteOnce"
    ReadWriteMany = "ReadWriteMany"
    ReadOnlyMany = "ReadOnlyMany"


class SAMLLMHostStorage(SAMModel):
    """
    Spec.storage: the model volume, a PersistentVolumeClaim mounted at /models.

    It caches the weights, so that a restarted server does not download them again. The
    cluster's storage class provisions its PersistentVolume.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    accessMode: AccessMode | None = Field("ReadWriteOnce", title="Accessmode")
    """LLMHost.spec.storage.accessMode[str]: One of: ['ReadWriteOnce', 'ReadWriteMany', 'ReadOnlyMany']."""
    existingClaim: str | None = Field(None, title="Existingclaim")
    """
    LLMHost.spec.storage.existingClaim[str]: an existing PersistentVolumeClaim to mount, instead of creating one.

    Required when model.source is pvc.
    """
    retain: bool | None = Field(True, title="Retain")
    """
    LLMHost.spec.storage.retain[bool]: keep the volume, and its downloaded weights, on undeploy.

    It is always deleted when the LLMHost is deleted.
    """
    size: str | None = Field("50Gi", title="Size")
    """LLMHost.spec.storage.size[str]: e.g. 50Gi."""
    storageClass: str | None = Field(None, title="Storageclass")
    """LLMHost.spec.storage.storageClass[str]: defaults to the cluster's default class."""


class SAMLLMHostModel(SAMModel):
    """Spec.model: what is served, and where its weights come from."""

    model_config = ConfigDict(
        extra="forbid",
    )
    architecture: str | None = Field(None, title="Architecture")
    """LLMHost.spec.model.architecture[str]: e.g. llama, qwen3, gemma3."""
    capabilities: SAMLLMHostModelCapabilities | None = None
    """LLMHost.spec.model.capabilities[object]: what the model can do."""
    contextWindow: conint(ge=0) | None = Field(None, title="Contextwindow")
    """LLMHost.spec.model.contextWindow[int]: the model's maximum context, in tokens."""
    embeddingDimensions: conint(ge=0) | None = Field(None, title="Embeddingdimensions")
    """LLMHost.spec.model.embeddingDimensions[int]: for embedding models."""
    file: str | None = Field(None, title="File")
    """
    LLMHost.spec.model.file[str]: a single weights file within the repository, e.g. a GGUF file for llama_cpp.

    For ollama with a Hugging Face source, the quantization tag, e.g. Q4_K_M.
    """
    license: str | None = Field(None, title="License")
    """LLMHost.spec.model.license[str]: e.g. apache-2.0."""
    parameterCount: conint(ge=0) | None = Field(None, title="Parametercount")
    """LLMHost.spec.model.parameterCount[int]: the number of parameters."""
    quantization: Quantization | None = Field("none", title="Quantization")
    """
    LLMHost.spec.model.quantization[str]: the weights' precision.

    One of: ['none', 'fp32', 'fp16', 'bf16', 'fp8', 'mxfp4', 'int8', 'int4', 'gguf', 'awq', 'gptq'].
    """
    repository: str = Field(..., title="Repository")
    """LLMHost.spec.model.repository[str]: the model, in the source's terms: a Hugging Face repository id, e.g. Qwen/Qwen3-8B; an Ollama tag, e.g. llama3.1:8b; an S3 prefix, e.g. s3://bucket/models/qwen3; a URL; or, for pvc, a path within the volume."""
    revision: str | None = Field(None, title="Revision")
    """
    LLMHost.spec.model.revision[str]: a Hugging Face branch, tag or commit SHA.

    Pin a commit SHA for reproducible deployments. Defaults to main.
    """
    servedName: str | None = Field(None, title="Servedname")
    """
    LLMHost.spec.model.servedName[str]: the model name that clients send in their requests.

    Defaults to the LLMHost's name. Ollama always uses repository.
    """
    source: Source | None = Field("huggingface", title="Source")
    """
    LLMHost.spec.model.source[str]: where the weights come from.

    One of: ['huggingface', 'ollama', 's3', 'url', 'pvc'].
    """
    task: Task | None = Field("text-generation", title="Task")
    """
    LLMHost.spec.model.task[str]: what the model does.

    One of: ['text-generation', 'embedding'].
    """
    tokenSecret: str | None = Field(None, title="Tokensecret")
    """
    LLMHost.spec.model.tokenSecret[str]: the name of a Smarter Secret with a Hugging Face access token, for gated models, e.g. Llama and Gemma.

    You must also accept the model's license on huggingface.co.
    """


class SAMLLMHostSpec(SAMModel):
    """Smarter API LLMHost Manifest LLMHost.spec."""

    model_config = ConfigDict(
        extra="forbid",
    )
    compute: str | None = Field(None, title="Compute")
    """
    LLMHost.spec.compute[str]: the LLMHostCompute that the LLMHost runs on, e.g. gpu_l4_1x.

    Defaults to the cheapest one that its resources fit.
    """
    engine: SAMLLMHostEngineConfig
    """LLMHost.spec.engine[object]: the inference server."""
    healthCheck: SAMLLMHostHealthCheck | None = None
    """LLMHost.spec.healthCheck[object]: probes."""
    model: SAMLLMHostModel
    """LLMHost.spec.model[object]: what is served."""
    network: SAMLLMHostNetwork | None = None
    """LLMHost.spec.network[object]: reachability."""
    resources: SAMLLMHostResources | None = None
    """LLMHost.spec.resources[object]: compute."""
    scaling: SAMLLMHostScaling | None = None
    """LLMHost.spec.scaling[object]: replicas."""
    storage: SAMLLMHostStorage | None = None
    """LLMHost.spec.storage[object]: the model volume."""


class SAMLLMHost(SAMModel):
    """Smarter API Manifest - LLMHost."""

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
    metadata: SAMLLMHostMetadata
    """LLMHost.metadata[obj]: Required, the LLMHost metadata."""
    spec: SAMLLMHostSpec
    """LLMHost.spec[obj]: Required, the LLMHost specification."""
    status: SAMLLMHostStatus | None = None
    """
    LLMHost.status[obj]: Optional, Read-only.

    Stateful status information about the LLMHost.
    """
