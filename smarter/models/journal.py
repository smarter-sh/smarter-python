"""
Models of the Smarter Journal api contract: the envelope of every journaled response, its error body, and a journal entry.

The Smarter platform journals its api responses. Each one carries ``api`` (the api version, e.g.
``smarter.sh/v1``) and ``metadata`` (the command and the resource kind, which the platform calls
its "thing") beside its own ``data``, ``message`` or ``error``.

These models mirror ``smarter.lib.journal.contract.models`` in the Smarter platform, whose JSON
Schema is ``journal-contract.schema.json``. The SDK's tests validate the platform's schema against
them. See ``scripts/sync-contracts.sh``.
"""

from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import Field

from smarter.core.typing import SmarterJsonType

from .base import SmarterCamelModel, SmarterModel

DataT = TypeVar("DataT")


class SAMJournalApiMetadata(SmarterModel):
    """The ``metadata`` of a journaled response: its command and thing, and the key of its journal entry."""

    command: str = Field(..., description="The journal's command, e.g. apply.")
    thing: str = Field(..., description="The journal's thing, e.g. Guardrail. The string 'None' when there is none.")
    key: Optional[str] = Field(
        None, description="The key of the response's journal entry, when the journal is enabled."
    )


class SAMJournalApiErrorBody(SmarterModel):
    """The ``error`` of a journaled error response.

    Every error of the cli api has this shape.
    """

    errorClass: str = Field(..., description="The name of the exception's class, e.g. SAMBrokerErrorNotFound.")
    stacktrace: Optional[str] = Field(None, description="The server's stack trace, when the platform includes it.")
    description: Optional[str] = Field(None, description="A human-readable description of the error.")
    status: int = Field(..., description="The http status.")
    args: SmarterJsonType = Field(None, description="The exception's arguments, or the request's url.")
    cause: Optional[str] = Field(None, description="The exception's cause.")
    context: Optional[str] = Field(None, description="The exception's context, or the response's thing and command.")
    thing: Optional[str] = Field(None, description="The journal's thing, e.g. Guardrail.")
    command: Optional[str] = Field(None, description="The journal's command, e.g. describe.")


class SAMJournalApiEnvelope(SmarterModel):
    """The fields that every journaled response adds beside its own data."""

    api: str = Field("smarter.sh/v1", description='The api version, e.g. "smarter.sh/v1".')
    metadata: Optional[SAMJournalApiMetadata] = None


class SAMJournalApiErrorResponse(SAMJournalApiEnvelope):
    """The body of a journaled error response."""

    error: SAMJournalApiErrorBody


class SmarterJournaledResponse(SAMJournalApiEnvelope, Generic[DataT]):
    """
    A successful journaled response: the envelope, the response's ``data``, and an optional ``message``.

    ``data`` is typed by the endpoint, e.g. ``SmarterJournaledResponse[WhoAmI]``.
    """

    data: Optional[DataT] = None
    message: Optional[str] = Field(None, description="A human-readable message, e.g. 'LLMClient calculator applied'.")


class SmarterJournalMessage(SAMJournalApiEnvelope):
    """A journaled response that carries only a ``message``, e.g. the response of delete or deploy."""

    message: Optional[str] = None


class JournalEntry(SmarterCamelModel):
    """
    A Smarter Journal entry, as ``/api/v1/journal/`` returns it.

    The list returns entries without ``request`` and ``response``. Retrieving one entry by its key
    includes them. Only superusers may read the journal, because the request documents hold the
    callers' credentials.
    """

    key: str
    created_at: Optional[datetime] = None
    user: Optional[str] = Field(None, description="The username of the caller, or None for an anonymous request.")
    thing: str
    command: str
    status_code: int
    request: SmarterJsonType = None
    response: SmarterJsonType = None


class JournalPagination(SmarterCamelModel):
    """The description of one page of the journal's entries."""

    page: int
    page_size: int
    num_pages: int
    count: int
    search: str = ""
    ordering: str = ""
    sort_fields: list[str] = []


class JournalPage(SmarterModel):
    """One page of the journal's entries."""

    objects: list[JournalEntry] = []
    pagination: JournalPagination


__all__ = [
    "JournalEntry",
    "JournalPage",
    "JournalPagination",
    "SAMJournalApiEnvelope",
    "SAMJournalApiErrorBody",
    "SAMJournalApiErrorResponse",
    "SAMJournalApiMetadata",
    "SmarterJournalMessage",
    "SmarterJournaledResponse",
]
