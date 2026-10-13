"""The history of chat sessions, tool calls and plugin uses: ``/api/v1/prompts/history/``, and the Smarter Journal."""

from __future__ import annotations

from typing import Optional

from smarter.core.typing import SmarterIdType
from smarter.models.journal import JournalEntry, JournalPage
from smarter.models.misc import PromptPluginUsage, PromptSession, PromptToolCall

from .base import SmarterAPIResource, resource_id


class PromptHistory(SmarterAPIResource):
    """
    The chat sessions of the api key's user, and their tool calls and plugin uses, newest first.

    An account admin also reads the sessions of their account's users, and a superuser every session.
    """

    path = "prompts/history/"

    def sessions(self) -> list[PromptSession]:
        """
        The chat sessions.

        :returns: The sessions.
        """
        return self._http.request("GET", f"{self.path}prompt/", cast_to=list[PromptSession])

    def session(self, id: SmarterIdType) -> PromptSession:  # pylint: disable=redefined-builtin
        """
        A chat session, by id.

        :param id: The session's id.
        :returns: The session.
        """
        return self._http.request("GET", f"{self.path}prompt/{resource_id(id)}/", cast_to=PromptSession)

    def tool_calls(self) -> list[PromptToolCall]:
        """
        The tool calls of the chat sessions, with the LLM requests that made them.

        :returns: The tool calls.
        """
        return self._http.request("GET", f"{self.path}tool-calls/", cast_to=list[PromptToolCall])

    def tool_call(self, id: SmarterIdType) -> PromptToolCall:  # pylint: disable=redefined-builtin
        """
        A tool call, by id.

        :param id: The tool call's id.
        :returns: The tool call.
        """
        return self._http.request("GET", f"{self.path}tool-calls/{resource_id(id)}/", cast_to=PromptToolCall)

    def plugin_usage(self) -> list[PromptPluginUsage]:
        """
        The plugin uses of the chat sessions.

        :returns: The plugin uses.
        """
        return self._http.request("GET", f"{self.path}plugin-usage/", cast_to=list[PromptPluginUsage])

    def plugin_use(self, id: SmarterIdType) -> PromptPluginUsage:  # pylint: disable=redefined-builtin
        """
        A plugin use, by id.

        :param id: The plugin use's id.
        :returns: The plugin use.
        """
        return self._http.request("GET", f"{self.path}plugin-usage/{resource_id(id)}/", cast_to=PromptPluginUsage)


class Journal(SmarterAPIResource):
    """
    The Smarter Journal: a record of every journaled api request and response.

    Superusers only.

    Each entry's request document holds the caller's headers, including their api key, so only
    superusers may read the journal.
    """

    path = "journal/"

    def list(
        self,
        *,
        page: int = 1,
        page_size: int | None = None,
        search: str | None = None,
        ordering: str | None = None,
    ) -> JournalPage:
        """
        One page of the journal's entries, newest first, without their request and response documents.

        :param page: The page number, from 1.
        :param page_size: Entries per page, or None for the platform's default.
        :param search: Only entries whose key, thing or command contains this text.
        :param ordering: A sort field, e.g. ``createdAt`` or ``-statusCode``.
        :returns: The page, and its pagination.
        """
        return self._http.request(
            "GET",
            self.path,
            params={"page": page, "page_size": page_size, "search": search, "ordering": ordering},
            cast_to=JournalPage,
        )

    def retrieve(self, key: str) -> JournalEntry:
        """
        A journal entry, with its request and response documents.

        :param key: The entry's key: the ``metadata.key`` of a journaled response.
        :returns: The entry.
        """
        return self._http.request("GET", f"{self.path}{resource_id(key)}/", cast_to=JournalEntry)


__all__ = ["Journal", "PromptHistory"]
