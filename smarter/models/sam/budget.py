"""
SAM model of the ``Budget`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import Field, confloat, conint, constr

from smarter.models.sam.base import SAMModel


class SAMBudgetMetadata(SAMModel):
    """Smarter API Budget Manifest - Metadata class."""

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


class Action(Enum):
    """Budget.spec.config.action: block further charges when a limit is reached, or only warn."""

    block = "block"
    warn = "warn"


class Period(Enum):
    """Budget.spec.config.period: the billing period of periodicLimit and duration."""

    hour = "hour"
    day = "day"
    week = "week"
    month = "month"


class Unit(Enum):
    """Budget.spec.config.unit: what the limits measure: cost in USD, or total tokens."""

    cost = "cost"
    tokens = "tokens"


class SAMBudgetSpecConfig(SAMModel):
    """Smarter API Budget Manifest Budget.spec.config: the budget's limits."""

    absoluteLimit: confloat(ge=0.0) | str | None = Field("0", title="Absolutelimit")
    """
    Budget.spec.config.absoluteLimit: the most that may be spent in total, from when the budget is attached.

    0 means no limit.
    """
    action: Action | None = Field("block", title="Action")
    """Budget.spec.config.action: block further charges when a limit is reached, or only warn."""
    duration: conint(ge=0) | None = Field(0, title="Duration")
    """
    Budget.spec.config.duration: the billing periods, from when the budget is attached, after which it no longer applies.

    0 means never.
    """
    message: constr(max_length=1000) | None = Field(None, title="Message")
    """
    Budget.spec.config.message: what people are told when the budget blocks their request.

    Defaults to a description of the limit that was reached.
    """
    period: Period | None = Field("month", title="Period")
    """Budget.spec.config.period: the billing period of periodicLimit and duration."""
    periodicLimit: confloat(ge=0.0) | str | None = Field("0", title="Periodiclimit")
    """
    Budget.spec.config.periodicLimit: the most that may be spent in a billing period.

    0 means no limit.
    """
    unit: Unit | None = Field("cost", title="Unit")
    """Budget.spec.config.unit: what the limits measure: cost in USD, or total tokens."""
    warningThreshold: conint(ge=0, le=100) | None = Field(80, title="Warningthreshold")
    """
    Budget.spec.config.warningThreshold: the percentage of a limit at which a warning is sent.

    0 means never.
    """


class Kind(Enum):
    """Budget.spec.resources.kind: the resource's manifest kind, e.g. LLMClient."""

    Account = "Account"
    User = "User"
    ApiConnection = "ApiConnection"
    SqlConnection = "SqlConnection"
    LLMClient = "LLMClient"
    LLMHost = "LLMHost"
    LLMHostCompute = "LLMHostCompute"
    MCPClient = "MCPClient"
    Orchestrator = "Orchestrator"
    Provider = "Provider"
    Proxy = "Proxy"
    Vectorsearch = "Vectorsearch"
    ApiPlugin = "ApiPlugin"
    SkillPlugin = "SkillPlugin"
    SqlPlugin = "SqlPlugin"
    StaticPlugin = "StaticPlugin"
    WebsearchPlugin = "WebsearchPlugin"
    ImageSearchPlugin = "ImageSearchPlugin"


class SAMBudgetSpecResource(SAMModel):
    """
    Smarter API Budget Manifest Budget.spec.resources[]: a resource that the budget is enforced on.

    Either kind and name, with an optional accountNumber, or a recordLocator.
    """

    accountNumber: str | None = Field(None, title="Accountnumber")
    """
    Budget.spec.resources.accountNumber: the account that the resource belongs to.

    Defaults to your own.
    """
    kind: Kind | None = Field(None, title="Kind")
    """Budget.spec.resources.kind: the resource's manifest kind, e.g. LLMClient."""
    name: str | None = Field(None, title="Name")
    """
    Budget.spec.resources.name: the resource's name.

    For an Account, its account number; for a User, the username.
    """
    recordLocator: str | None = Field(None, title="Recordlocator")
    """Budget.spec.resources.recordLocator: any resource's record locator, e.g. llmclient-rc2x, in place of kind and name."""


class SAMBudgetStatusResource(SAMModel):
    """
    The budget versus the actual spending of one of the budget's resources.

    Read only.
    """

    absoluteActual: float | str = Field(..., title="Absoluteactual")
    """Budget.status.resources.absoluteActual: spending since startDate."""
    absolutePercent: float | None = Field(None, title="Absolutepercent")
    """Budget.status.resources.absolutePercent: absoluteActual, as a percentage of the limit."""
    expiresAt: datetime | None = Field(None, title="Expiresat")
    """Budget.status.resources.expiresAt: when the budget's duration ends."""
    isActive: bool = Field(..., title="Isactive")
    """Budget.status.resources.isActive: whether the budget is enforced on it."""
    isLocked: bool = Field(..., title="Islocked")
    """Budget.status.resources.isLocked: whether the budget refuses further charges."""
    lockReason: str | None = Field(None, title="Lockreason")
    """Budget.status.resources.lockReason: which limit was reached."""
    periodicActual: float | str = Field(..., title="Periodicactual")
    """Budget.status.resources.periodicActual: spending this billing period."""
    periodicPercent: float | None = Field(None, title="Periodicpercent")
    """Budget.status.resources.periodicPercent: periodicActual, as a percentage of the limit."""
    recordLocator: str = Field(..., title="Recordlocator")
    """Budget.status.resources.recordLocator: the resource's record locator."""
    startDate: datetime = Field(..., title="Startdate")
    """Budget.status.resources.startDate: when the budget was attached."""


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


class SAMBudgetSpec(SAMModel):
    """Smarter API Budget Manifest Budget.spec."""

    config: SAMBudgetSpecConfig
    """
    Budget.spec.config[object].

    The limits of the Budget.
    """
    resources: list[SAMBudgetSpecResource] | None = Field(None, max_length=1000, title="Resources")
    """
    Budget.spec.resources[list].

    The resources that the Budget is enforced on. Resources that are removed from the list are detached.
    """


class SAMBudgetStatus(SAMModel):
    """
    Smarter API Budget Manifest - Status class.

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
    resources: list[SAMBudgetStatusResource] | None = Field(None, title="Resources")
    """
    Budget.status.resources: the budget versus the actual spending of each resource.

    Read only.
    """


class SAMBudget(SAMModel):
    """Smarter API Manifest - Budget."""

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
    metadata: SAMBudgetMetadata
    """Budget.metadata[obj]: Required, the Budget metadata."""
    spec: SAMBudgetSpec
    """Budget.spec[obj]: Required, the Budget specification."""
    status: SAMBudgetStatus | None = None
    """
    Budget.status[obj]: Optional, Read-only.

    Stateful status information about the Budget.
    """
