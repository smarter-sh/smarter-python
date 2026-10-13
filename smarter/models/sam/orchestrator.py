"""
SAM model of the ``Orchestrator`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Optional, Union
from uuid import UUID

from pydantic import Field, conint, constr

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
    llmClientName: str = Field(..., title="Llmclientname")
    """Name of an existing LLMClient to attach as a Harness."""
    role: HarnessRole | None = "executor"


class SAMOrchestratorMetadata(SAMModel):
    """Smarter API Orchestrator Manifest - Metadata class."""

    annotations: None | (
        list[
            dict[
                str,
                (
                    str
                    | int
                    | float
                    | bool
                    | date
                    | datetime
                    | constr(pattern=r"^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$")
                    | UUID
                    | bytes
                    | list
                    | dict[str, Any]
                ),
            ]
        ]
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
    maxIterations: conint(ge=1) | None = Field(10, title="Maxiterations")
    """Upper bound on orchestration loop iterations."""
    strategy: OrchestrationStrategy | None = "sequential"


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
