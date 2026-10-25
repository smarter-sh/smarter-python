"""Models of guardrails, their evaluations, and their events."""

from datetime import datetime

from pydantic import Field

from smarter.core.typing import SmarterJsonObjectType

from .base import SmarterCamelModel, SmarterModel, SmarterResource


class Guardrail(SmarterResource):
    """A guardrail: a check that the platform runs on prompts (``input``) or on the LLM's replies (``output``)."""

    stage: str | None = Field(None, description="input or output.")
    category: str | None = None
    strategy: str | None = Field(None, description="e.g. regex, detector, classifier or llm.")
    pattern: str | None = None
    config: SmarterJsonObjectType | None = None
    threshold: float | None = None
    action: str | None = Field(None, description="e.g. block, redact or flag.")
    replacement: str | None = None
    message: str | None = None
    severity: int | None = None
    mode: str | None = Field(None, description="enforce or monitor.")
    fail_closed: bool | None = None
    priority: int | None = None
    is_active: bool | None = None


class GuardrailMatch(SmarterModel):
    """A span of the text that a guardrail matched."""

    start: int
    end: int
    text: str
    label: str | None = None


class GuardrailFinding(SmarterModel):
    """One finding of a guardrail evaluation."""

    confidence: float | None = None
    rationale: str | None = None
    matches: list[GuardrailMatch] = []


class GuardrailEvaluation(SmarterCamelModel):
    """
    The result of a guardrail's dry run on a text.

    Nothing is saved: an evaluation does not create an event.
    """

    guardrail: str
    stage: str
    triggered: bool
    disposition: str | None = Field(None, description="e.g. passed, blocked, redacted or flagged.")
    text: str | None = Field(None, description="The text after the guardrail's action, e.g. redacted.")
    message: str | None = None
    error: str | None = None
    duration_ms: float | None = None
    findings: list[GuardrailFinding] = []


class GuardrailEvent(SmarterCamelModel):
    """A guardrail's finding in a real prompt, saved for review."""

    id: int
    created_at: datetime | None = None
    llmclient: str | None = Field(None, description="The name of the LLMClient whose prompt triggered it.")
    stage: str | None = None
    disposition: str | None = None
    reviewed: bool | None = None


class GuardrailEvents(SmarterModel):
    """The latest events of a guardrail."""

    guardrail: str
    events: list[GuardrailEvent] = []


__all__ = [
    "Guardrail",
    "GuardrailEvaluation",
    "GuardrailEvent",
    "GuardrailEvents",
    "GuardrailFinding",
    "GuardrailMatch",
]
