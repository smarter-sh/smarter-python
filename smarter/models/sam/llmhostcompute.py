"""
SAM model of the ``LLMHostCompute`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import ConfigDict, Field, confloat, conint, constr

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


class SAMLLMHostComputeCost(SAMModel):
    """Spec.cost: the price of one node, from which LLMHosts' costs are reported."""

    model_config = ConfigDict(
        extra="forbid",
    )
    currency: str | None = Field("USD", title="Currency")
    """LLMHostCompute.spec.cost.currency[str]: e.g. USD."""
    perHour: confloat(ge=0.0) | str | None = Field(None, title="Perhour")
    """LLMHostCompute.spec.cost.perHour[decimal]: the cost per hour of one node, e.g. its on-demand price."""


class SAMLLMHostComputeGpu(SAMModel):
    """Spec.node.gpu: the node's GPUs."""

    model_config = ConfigDict(
        extra="forbid",
    )
    count: conint(ge=1, le=16) = Field(..., title="Count")
    """LLMHostCompute.spec.node.gpu.count[int]: the node's GPUs."""
    memoryGb: conint(ge=1) = Field(..., title="Memorygb")
    """LLMHostCompute.spec.node.gpu.memoryGb[int]: the memory of one GPU, in GB."""
    resource: str | None = Field("nvidia.com/gpu", title="Resource")
    """LLMHostCompute.spec.node.gpu.resource[str]: the Kubernetes extended resource that advertises the GPUs."""
    type: str = Field(..., title="Type")
    """LLMHostCompute.spec.node.gpu.type[str]: the GPU model, e.g. L4, A10G, H100-80GB."""


class SAMLLMHostComputeMetadata(SAMModel):
    """Smarter API LLMHostCompute Manifest - Metadata class."""

    annotations: dict[str, str] | None = Field(
        None,
        examples=[{"acme.com/crm-account-id": "A-10042", "smarter.sh/llmclient/use-case": "customer support"}],
        title="Annotations",
    )
    """
    Annotations, as in Kubernetes: a map of keys to string values that clients and integrations attach to a resource for their own purposes, e.g. to associate it with a resource in another system.

    A key is an optional DNS-subdomain prefix that names its owner, then a slash and a name of one or more slash-separated segments, e.g. 'acme.com/crm-account-id'. The prefix 'smarter.sh' and its subdomains are reserved for the Smarter platform. Values are strings: unquoted YAML scalars such as true, 42 or dates are converted to strings, and structured data belongs in a JSON string. All annotations together are limited to 256 KiB. The list of one-key maps of older manifests, e.g. [{'acme.com/crm-account-id': 'A-10042'}], is also accepted.
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


class SAMLLMHostComputeNode(SAMModel):
    """Spec.node: the kind of node."""

    model_config = ConfigDict(
        extra="forbid",
    )
    amiType: str | None = Field(None, title="Amitype")
    """
    LLMHostCompute.spec.node.amiType[str]: e.g. AL2023_x86_64_NVIDIA.

    Defaults to the NVIDIA AMI for a GPU node, else the standard AMI.
    """
    capacityType: constr(pattern=r"^(ON_DEMAND|SPOT)$") | None = Field("ON_DEMAND", title="Capacitytype")
    """LLMHostCompute.spec.node.capacityType[str]: ON_DEMAND or SPOT."""
    cpu: conint(ge=1) = Field(..., title="Cpu")
    """LLMHostCompute.spec.node.cpu[int]: the node's vCPUs."""
    diskSizeGb: conint(ge=20) | None = Field(100, title="Disksizegb")
    """
    LLMHostCompute.spec.node.diskSizeGb[int]: the node's root volume, for container images.

    Model weights are on the LLMHosts' own volumes.
    """
    gpu: SAMLLMHostComputeGpu | None = None
    """
    LLMHostCompute.spec.node.gpu[object]: the node's GPUs.

    None for a CPU node.
    """
    instanceType: str = Field(..., title="Instancetype")
    """LLMHostCompute.spec.node.instanceType[str]: e.g. g6.2xlarge."""
    memoryGb: conint(ge=1) = Field(..., title="Memorygb")
    """LLMHostCompute.spec.node.memoryGb[int]: the node's memory, in GiB."""


class SAMLLMHostComputeNodeGroup(SAMModel):
    """Spec.nodeGroup: the node group of the nodes."""

    model_config = ConfigDict(
        extra="forbid",
    )
    maxNodes: conint(ge=1, le=100) | None = Field(4, title="Maxnodes")
    """LLMHostCompute.spec.nodeGroup.maxNodes[int]: the most nodes that Smarter adds to the node group."""
    subnetIds: list[str] | None = Field(None, title="Subnetids")
    """
    LLMHostCompute.spec.nodeGroup.subnetIds[list]: the node group's subnets.

    Defaults to the platform's. One subnet keeps the nodes in one availability zone, with the LLMHosts' model volumes.
    """


class SAMLLMHostComputeSpec(SAMModel):
    """Smarter API LLMHostCompute Manifest LLMHostCompute.spec."""

    model_config = ConfigDict(
        extra="forbid",
    )
    cost: SAMLLMHostComputeCost | None = None
    """LLMHostCompute.spec.cost[object]: for reporting."""
    node: SAMLLMHostComputeNode
    """LLMHostCompute.spec.node[object]: the kind of node."""
    nodeGroup: SAMLLMHostComputeNodeGroup | None = None
    """LLMHostCompute.spec.nodeGroup[object]: the node group of the nodes."""


class SAMLLMHostComputeStatus(SAMModel):
    """
    Smarter API LLMHostCompute Manifest - Status class.

    Read only. Besides ownership, it reports the node group, as of its most recent reconcile.
    """

    accountNumber: str = Field(..., title="Accountnumber")
    """
    LLMHostCompute.status.account_number: The account owner of this LLMHostCompute.

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
    desiredNodes: int | None = Field(None, title="Desirednodes")
    """LLMHostCompute.status.desiredNodes: the node group's desired size. Read only."""
    lastReconciledAt: datetime | None = Field(None, title="Lastreconciledat")
    """
    LLMHostCompute.status.lastReconciledAt: when it was last reconciled.

    Read only.
    """
    llmhosts: int | None = Field(None, title="Llmhosts")
    """
    LLMHostCompute.status.llmhosts: the LLMHosts that run on it.

    Read only.
    """
    message: str | None = Field(None, title="Message")
    """LLMHostCompute.status.message: the result of the last reconcile. Read only."""
    modified: datetime = Field(..., title="Modified")
    """
    The date in which this resource was most recently changed.

    Read only.
    """
    nodeGroupName: str | None = Field(None, title="Nodegroupname")
    """
    LLMHostCompute.status.nodeGroupName: the cloud's name of the node group.

    Read only.
    """
    nodeGroupStatus: str | None = Field(None, title="Nodegroupstatus")
    """
    LLMHostCompute.status.nodeGroupStatus: e.g. absent, CREATING or ACTIVE.

    Read only.
    """
    readyNodes: int | None = Field(None, title="Readynodes")
    """
    LLMHostCompute.status.readyNodes: the nodes that have joined the cluster.

    Read only.
    """
    recordLocator: str = Field(..., title="Recordlocator")
    """
    RecordLocator[String]: An optional identifier used to locate the resource record associated with this manifest.

    Read only.
    """
    username: str = Field(..., title="Username")
    """
    LLMHostCompute.status.username: The Smarter user who created this LLMHostCompute.

    Read only.
    """


class SAMLLMHostCompute(SAMModel):
    """Smarter API Manifest - LLMHostCompute."""

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
    metadata: SAMLLMHostComputeMetadata
    """LLMHostCompute.metadata[obj]: Required, the LLMHostCompute metadata."""
    spec: SAMLLMHostComputeSpec
    """LLMHostCompute.spec[obj]: Required, the LLMHostCompute specification."""
    status: SAMLLMHostComputeStatus | None = None
    """
    LLMHostCompute.status[obj]: Optional, Read-only.

    Stateful status information about the LLMHostCompute.
    """
