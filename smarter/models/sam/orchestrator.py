"""
SAM model of the ``Orchestrator`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field, conint

from smarter.models.sam.base import SAMModel


class HarnessRole(Enum):
    """
    Role an LLMClient (Harness) plays within an Orchestrator.

    Values must stay aligned with
    smarter.apps.orchestrator.models.OrchestratorHarness.Role.
    """

    planner = "planner"
    executor = "executor"
    critic = "critic"
    router = "router"
    summarizer = "summarizer"
    tool_caller = "tool_caller"


class OrchestrationStrategy(Enum):
    """
    Coordination pattern the Orchestrator applies across its member LLMClients.

    Values must stay aligned with
    smarter.apps.orchestrator.models.OrchestrationStrategy.
    """

    sequential = "sequential"
    parallel = "parallel"
    supervisor = "supervisor"
    router = "router"
    voting = "voting"
    debate = "debate"


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


class SAMOrchestratorHarnessConfig(SAMModel):
    """
    A single LLMClient (Harness) membership within the Orchestrator.

    Mirrors smarter.apps.orchestrator.models.OrchestratorHarness. The
    llmClientName is a reference by name, not by primary key — resolved
    against the account's existing LLMClients at apply time.
    """

    config: dict[str, Any] | None = Field(None, title="Config")
    """Per-membership overrides (e.g. temperature, system prompt fragment, tool allowlist)."""
    executionOrder: conint(ge=0) | None = Field(0, title="Executionorder")
    """Relative ordering for sequential/supervisor strategies."""
    isActive: bool | None = Field(True, title="Isactive")
    """Whether this LLMClient's membership in the Orchestrator is active."""
    llmClientName: str = Field(..., title="Llmclientname")
    """Name of an existing LLMClient to attach as a Harness."""
    role: HarnessRole | None = "executor"
    """
    The part this LLMClient plays in the Orchestrator: planner, executor, critic, router, summarizer or tool_caller.

    The supervisor strategy needs a planner, and the router strategy a router.
    """


class SAMOrchestratorMetadata(SAMModel):
    """Smarter API Orchestrator Manifest - Metadata class."""

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


class SAMOrchestratorSpecConfig(SAMModel):
    """
    Spec block for an Orchestrator SAM manifest.

    Mirrors smarter.apps.orchestrator.models.Orchestrator. Consumed by the
    manifest controller to create/update the corresponding Orchestrator
    model instance and its OrchestratorHarness memberships.
    """

    harnesses: list[SAMOrchestratorHarnessConfig] = Field(..., min_length=1, title="Harnesses")
    """LLMClients (Harnesses) that participate in this Orchestrator."""
    isActive: bool | None = Field(True, title="Isactive")
    """Whether the Orchestrator is active."""
    maxIterations: conint(ge=1) | None = Field(10, title="Maxiterations")
    """Upper bound on orchestration loop iterations."""
    strategy: OrchestrationStrategy | None = "sequential"
    """
    How the Orchestrator coordinates its LLMClients: sequential, parallel, supervisor, router, voting or debate.

    Supervisor needs a harness with role planner, router one with role router, and voting and debate at least two harnesses.
    """


class SAMOrchestratorStatus(SAMModel):
    """Smarter API Orchestrator Manifest - Status class."""

    accountNumber: str = Field(..., title="Accountnumber")
    """
    Orchestrator.status.account_number: The account owner of this Orchestrator.

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
    modified: datetime = Field(..., title="Modified")
    """
    The date in which this resource was most recently changed.

    Read only.
    """
    recordLocator: str = Field(..., title="Recordlocator")
    """
    RecordLocator[String]: An optional identifier used to locate the resource record associated with this manifest.

    Read only.
    """
    username: str = Field(..., title="Username")
    """
    Orchestrator.status.username: The Smarter user who created this Orchestrator.

    Read only.
    """


class SAMOrchestratorSpec(SAMModel):
    """Smarter API Orchestrator Manifest Orchestrator.spec."""

    config: SAMOrchestratorSpecConfig
    """
    Orchestrator.spec.config[object].

    The configuration for the Orchestrator.
    """


class SAMOrchestrator(SAMModel):
    """Smarter API Manifest - Orchestrator."""

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
    metadata: SAMOrchestratorMetadata
    """Orchestrator.metadata[obj]: Required, the Orchestrator metadata."""
    spec: SAMOrchestratorSpec
    """Orchestrator.spec[obj]: Required, the Orchestrator specification."""
    status: SAMOrchestratorStatus | None = None
    """
    Orchestrator.status[obj]: Optional, Read-only.

    Stateful status information about the Orchestrator.
    """
