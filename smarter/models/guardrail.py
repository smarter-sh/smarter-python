"""Models of guardrails, their evaluations, and their events."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from smarter.core.typing import SmarterJsonObjectType

from .base import SmarterCamelModel, SmarterModel, SmarterResource


class Guardrail(SmarterResource):
    """A guardrail: a check that the platform runs on prompts (``input``) or on the LLM's replies (``output``)."""

    stage: Optional[str] = Field(None, description="input or output.")
    category: Optional[str] = None
    strategy: Optional[str] = Field(None, description="e.g. regex, detector, classifier or llm.")
    pattern: Optional[str] = None
    config: Optional[SmarterJsonObjectType] = None
    threshold: Optional[float] = None
    action: Optional[str] = Field(None, description="e.g. block, redact or flag.")
    replacement: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[int] = None
    mode: Optional[str] = Field(None, description="enforce or monitor.")
    fail_closed: Optional[bool] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class GuardrailMatch(SmarterModel):
    """A span of the text that a guardrail matched."""

    start: int
    end: int
    text: str
    label: Optional[str] = None


class GuardrailFinding(SmarterModel):
    """One finding of a guardrail evaluation."""

    confidence: Optional[float] = None
    rationale: Optional[str] = None
    matches: list[GuardrailMatch] = []


class GuardrailEvaluation(SmarterCamelModel):
    """
    The result of a guardrail's dry run on a text.

    Nothing is saved: an evaluation does not create an event.
    """

    guardrail: str
    stage: str
    triggered: bool
    disposition: Optional[str] = Field(None, description="e.g. passed, blocked, redacted or flagged.")
    text: Optional[str] = Field(None, description="The text after the guardrail's action, e.g. redacted.")
    message: Optional[str] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None
    findings: list[GuardrailFinding] = []


class GuardrailEvent(SmarterCamelModel):
    """A guardrail's finding in a real prompt, saved for review."""

    id: int
    created_at: Optional[datetime] = None
    llmclient: Optional[str] = Field(None, description="The name of the LLMClient whose prompt triggered it.")
    stage: Optional[str] = None
    disposition: Optional[str] = None
    reviewed: Optional[bool] = None


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
