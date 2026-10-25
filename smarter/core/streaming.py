"""
A parser of Server-Sent Events.

The Smarter prompt api streams a prompt's progress as Server-Sent Events when the request's
``Accept`` header includes ``text/event-stream``: ``progress`` events while it runs, then one
``result`` event with the same JSON as a non-streaming response.
"""

import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from smarter.core.typing import SmarterJsonType

EVENT_STREAM_CONTENT_TYPE = "text/event-stream"


@dataclass(frozen=True)
class ServerSentEvent:
    """
    One Server-Sent Event.

    :param event: The event's type, e.g. ``progress``, or None for an unnamed event.
    :param data: The event's data: its ``data:`` lines, joined by newlines.
    :param id: The event's id, if any.
    :param retry: The reconnection time that the server asked for, in milliseconds, if any.
    """

    event: str | None
    data: str
    id: str | None = None
    retry: int | None = None

    def json(self) -> SmarterJsonType:
        """
        The event's data, parsed as JSON.

        :returns: The parsed data.
        :raises json.JSONDecodeError: If the data is not JSON.
        """
        return json.loads(self.data)


def iter_sse(lines: Iterable[str]) -> Iterator[ServerSentEvent]:
    """
    Parse a stream's lines into events, as the HTML Living Standard specifies.

    A blank line ends an event. Comments (lines that start with ``:``), and blocks that set only
    ``retry``, yield nothing.

    :param lines: The stream's lines, without their line endings.
    :returns: The events, in order.
    """
    event: str | None = None
    data: list[str] = []
    event_id: str | None = None
    retry: int | None = None
    for line in lines:
        if line == "":
            if data or event:
                yield ServerSentEvent(event=event, data="\n".join(data), id=event_id, retry=retry)
            event, data, event_id, retry = None, [], None, None
            continue
        if line.startswith(":"):
            continue
        field, _, value = line.partition(":")
        value = value[1:] if value.startswith(" ") else value
        if field == "event":
            event = value
        elif field == "data":
            data.append(value)
        elif field == "id":
            event_id = value
        elif field == "retry" and value.isdigit():
            retry = int(value)
    if data or event:
        yield ServerSentEvent(event=event, data="\n".join(data), id=event_id, retry=retry)


__all__ = ["EVENT_STREAM_CONTENT_TYPE", "ServerSentEvent", "iter_sse"]
