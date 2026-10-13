"""
SAM model of the ``Guardrail`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional, Union
from uuid import UUID

from pydantic import Field, confloat, conint, constr

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


class SAMGuardrailMetadata(SAMModel):
    """Smarter API Guardrail Manifest - Metadata class."""

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


class SAMGuardrailSpecConfig(SAMModel):
    """Smarter API Guardrail Manifest Guardrail.spec.config."""

    action: str = Field(..., title="Action")
    """
    Guardrail.spec.config.action[str]: what the guardrail does when it triggers.

    One of: ['log', 'flag', 'redact', 'transform', 'block', 'escalate'].
    """
    caseSensitive: bool | None = Field(False, title="Casesensitive")
    """Guardrail.spec.config.caseSensitive[bool]: whether the keyword strategy is case sensitive."""
    categories: list[str] | None = Field(None, title="Categories")
    """
    Guardrail.spec.config.categories[list]: the moderation strategy's categories.

    Empty means all. Any of: ['harassment', 'harassment/threatening', 'hate', 'hate/threatening', 'illicit', 'illicit/violent', 'self-harm', 'self-harm/intent', 'self-harm/instructions', 'sexual', 'sexual/minors', 'violence', 'violence/graphic'].
    """
    category: str | None = Field("custom", title="Category")
    """
    Guardrail.spec.config.category[str]: the risk the guardrail addresses.

    One of: ['pii', 'secrets', 'prompt_injection', 'jailbreak', 'toxicity', 'self_harm', 'hallucination', 'off_topic', 'compliance', 'formatting', 'custom'].
    """
    detectors: list[str] | None = Field(None, title="Detectors")
    """
    Guardrail.spec.config.detectors[list]: the detector strategy's detectors.

    Any of: ['credit_card', 'us_ssn', 'email', 'phone_number', 'ip_address', 'iban', 'aws_access_key', 'private_key', 'api_key', 'jwt', 'password_assignment'].
    """
    failClosed: bool | None = Field(False, title="Failclosed")
    """
    Guardrail.spec.config.failClosed[bool]: if true, block when the check itself fails, e.g. because the LLM provider is unavailable.

    If false, the failure is recorded, and the prompt continues.
    """
    flags: list[str] | None = Field(None, title="Flags")
    """
    Guardrail.spec.config.flags[list]: the regex strategy's flags.

    Any of: ['IGNORECASE', 'MULTILINE', 'DOTALL'].
    """
    isActive: bool | None = Field(True, title="Isactive")
    """Guardrail.spec.config.isActive[bool]: whether the guardrail runs."""
    judgePrompt: str | None = Field(None, title="Judgeprompt")
    """
    Guardrail.spec.config.judgePrompt[str]: the llm_judge strategy's prompt, with a {text} placeholder for the text to judge.

    Any other braces must be doubled, e.g. {{ and }}.
    """
    keywords: list[str] | None = Field(None, title="Keywords")
    """Guardrail.spec.config.keywords[list]: the keyword strategy's words and phrases."""
    message: str | None = Field(None, title="Message")
    """Guardrail.spec.config.message[str]: what block returns to the user, instead of the LLM's reply."""
    mode: str | None = Field("enforce", title="Mode")
    """Guardrail.spec.config.mode[str]: enforce, to take the action, or monitor, to only record what the action would have been."""
    model: str | None = Field(None, title="Model")
    """Guardrail.spec.config.model[str]: the model of the semantic, moderation and llm_judge strategies."""
    pattern: str | None = Field(None, title="Pattern")
    """Guardrail.spec.config.pattern[str]: the regex strategy's regular expression."""
    priority: conint(ge=0) | None = Field(100, title="Priority")
    """
    Guardrail.spec.config.priority[int]: the order in which guardrails run.

    Lower runs first.
    """
    provider: str | None = Field(None, title="Provider")
    """
    Guardrail.spec.config.provider[str]: the name of the Smarter LLM Provider that the semantic, moderation and llm_judge strategies call.

    Defaults to openai.
    """
    referenceTexts: list[str] | None = Field(None, title="Referencetexts")
    """Guardrail.spec.config.referenceTexts[list]: the semantic strategy's examples of what to detect."""
    replacement: str | None = Field(None, title="Replacement")
    """
    Guardrail.spec.config.replacement[str]: what redact and transform replace each match with.

    Defaults to [REDACTED], which an empty replacement also means. {label} is replaced with what matched, e.g. credit_card. For the regex strategy, transform may refer to groups, e.g. \1.
    """
    severity: conint(ge=1, le=5) | None = Field(3, title="Severity")
    """Guardrail.spec.config.severity[int]: from 1 (low) to 5 (critical), for reporting and review."""
    stage: str = Field(..., title="Stage")
    """
    Guardrail.spec.config.stage[str]: when the guardrail runs.

    One of: ['input', 'output', 'both'].
    """
    strategy: str = Field(..., title="Strategy")
    """
    Guardrail.spec.config.strategy[str]: how the guardrail detects.

    One of: ['regex', 'keyword', 'detector', 'semantic', 'moderation', 'llm_judge'].
    """
    threshold: confloat(ge=0.0, le=1.0) | None = Field(None, title="Threshold")
    """
    Guardrail.spec.config.threshold[float]: the minimum confidence, from 0 to 1, at which the semantic, moderation and llm_judge strategies trigger.

    Defaults to 0.8.
    """
    wholeWord: bool | None = Field(True, title="Wholeword")
    """Guardrail.spec.config.wholeWord[bool]: whether the keyword strategy matches whole words only."""


class SAMGuardrailStatus(SAMModel):
    """
    Smarter API Guardrail Manifest - Status class.

    Read only. Besides ownership, it reports the guardrail's events of the last 30 days. The
    LLMClients that use it are reported in ``dependencies``.
    """

    accountNumber: str = Field(..., title="Accountnumber")
    """
    Guardrail.status.account_number: The account owner of this Guardrail.

    Read only.
    """
    blocked: int | None = Field(None, title="Blocked")
    """
    Guardrail.status.blocked: how many prompts this Guardrail blocked in the last 30 days.

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
    errors: int | None = Field(None, title="Errors")
    """
    Guardrail.status.errors: how many times this Guardrail failed to run in the last 30 days.

    Read only.
    """
    lastTriggered: datetime | None = Field(None, title="Lasttriggered")
    """
    Guardrail.status.lastTriggered: when this Guardrail last triggered.

    Read only.
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
    triggered: int | None = Field(None, title="Triggered")
    """
    Guardrail.status.triggered: how many times this Guardrail triggered in the last 30 days.

    Read only.
    """
    username: str = Field(..., title="Username")
    """
    Guardrail.status.username: The Smarter user who created this Guardrail.

    Read only.
    """


class SAMGuardrailSpec(SAMModel):
    """Smarter API Guardrail Manifest Guardrail.spec."""

    config: SAMGuardrailSpecConfig
    """
    Guardrail.spec.config[object].

    The configuration for the Guardrail.
    """


class SAMGuardrail(SAMModel):
    """Smarter API Manifest - Guardrail."""

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
    metadata: SAMGuardrailMetadata
    """Guardrail.metadata[obj]: Required, the Guardrail metadata."""
    spec: SAMGuardrailSpec
    """Guardrail.spec[obj]: Required, the Guardrail specification."""
    status: SAMGuardrailStatus | None = None
    """
    Guardrail.status[obj]: Optional, Read-only.

    Stateful status information about the Guardrail.
    """
