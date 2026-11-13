"""
Models of a user's token usage and data exports, under ``/api/v1/accounts/``.

The token usage is snake_case JSON, and the data exports camelCase.
"""

from datetime import datetime

from pydantic import Field

from .base import SmarterCamelModel, SmarterModel


class TokenUsagePoint(SmarterModel):
    """The tokens and cost of the user's LLM requests in one period: an hour, a day or a month."""

    period_start: datetime = Field(..., description="The start of the period, in UTC.")
    records: int = Field(0, description="How many charges the period has.")
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    total_cost: float = Field(0.0, description="The period's cost, in US dollars.")


class TokenUsage(SmarterModel):
    """The tokens and cost of the user's LLM requests over a window of time, one point per period, oldest first."""

    periodicity: str = Field(..., description="The window: 12_hours, 24_hours, 7_days, 1_month or 1_year.")
    period: str = Field(..., description="The period of each point: hour, day or month.")
    points: list[TokenUsagePoint] = []


class DataExport(SmarterCamelModel):
    """
    A data export's progress.

    An export is a zip file of the manifest of every resource that the user owns, in every account
    they belong to, with Secrets' values redacted. A link to it is emailed to the user when it is
    ready: the api never returns the link.
    """

    id: int
    status: str = Field(..., description="queued, running, succeeded or failed.")
    step: str = Field(..., description="queued, inventory, manifests, archive, upload, email or done.")
    resource_count: int = Field(0, description="How many resources the user owns.")
    manifest_count: int = Field(0, description="How many manifests have been written so far.")
    failed_count: int = Field(0, description="How many resources had no manifest.")
    size_bytes: int = Field(0, description="The size of the zip file.")
    email: str = Field("", description="The address that the link is emailed to.")
    created_at: datetime
    expires_at: datetime | None = Field(None, description="When the emailed link expires.")
    error: str = Field("", description="Why the export failed, or an empty string.")


class DataExportOverview(SmarterCamelModel):
    """What the user may export: where the link goes, the limits, and their latest export."""

    email: str = Field("", description="The address that the link is emailed to, or empty if there is none.")
    link_hours: int = Field(..., description="How many hours the emailed link works.")
    exports_per_day: int = Field(..., description="The most exports that a user may start in 24 hours.")
    exports_left_today: int = Field(..., description="How many more the user may start now.")
    latest: DataExport | None = Field(None, description="The user's most recent export, or None if there is none.")


__all__ = ["DataExport", "DataExportOverview", "TokenUsage", "TokenUsagePoint"]
