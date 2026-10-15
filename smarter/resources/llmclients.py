"""
LLMClients: read them, prompt them, stream a prompt's progress, and hold a multi-turn chat.

.. code-block:: python

    from smarter import Smarter

    client = Smarter()
    llmclient = client.llm_clients.find("calculator")

    # one prompt
    response = client.llm_clients.prompt(llmclient.id, "What is 17 times 23?")
    print(response.text)

    # a conversation, which keeps its session and thread
    chat = client.llm_clients.chat(llmclient.id)
    print(chat.send("What is 2 to the 10th power?").text)
    print(chat.send("And divided by 4?").text)

    # the prompt's progress, e.g. its tool calls, while it runs
    with client.llm_clients.stream(llmclient.id, "What is sin(pi / 2)?") as stream:
        for event in stream:
            print(event.message)
        print(stream.response.text)
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Optional, Union

from smarter.core.exceptions import SmarterError
from smarter.core.streaming import ServerSentEvent
from smarter.core.typing import SmarterIdType, SmarterJsonType
from smarter.models.chat import (
    LLM_MESSAGE_ROLES,
    PromptChatApiConfig,
    PromptChatApiConfigResponse,
    PromptChatApiErrorResponse,
    PromptChatApiMessage,
    PromptChatApiProgressEvent,
    PromptChatApiProgressResult,
    PromptChatApiPromptResponse,
)
from smarter.models.journal import SmarterJournalMessage
from smarter.models.llmclient import (
    LLMClient,
    LLMClientApiKey,
    LLMClientCustomDomain,
    LLMClientExtension,
    LLMClientPlugin,
)

from .base import SmarterKindResource, resource_id

MessageInput = Union[PromptChatApiMessage, Mapping[str, SmarterJsonType]]
"""A message: a :class:`PromptChatApiMessage`, or a dict such as ``{"role": "user", "content": "Hi"}``."""

PromptInput = Union[str, Sequence[MessageInput]]
"""A prompt: the text of one user message, or a list of messages."""


class SmarterPromptError(SmarterError):
    """
    A streamed prompt failed.

    Its ``result`` event carried an error response.

    :param message: The error's description.
    :param response: The error response.
    """

    def __init__(self, message: str, response: PromptChatApiPromptResponse | PromptChatApiErrorResponse):
        super().__init__(message)
        self.response = response


def to_messages(prompt: PromptInput) -> list[PromptChatApiMessage]:
    """
    A prompt as a list of messages.

    :param prompt: A user message's text, or a list of messages.
    :returns: The messages.
    """
    if isinstance(prompt, str):
        return [PromptChatApiMessage(role="user", content=prompt)]
    return [m if isinstance(m, PromptChatApiMessage) else PromptChatApiMessage.model_validate(m) for m in prompt]


def request_messages(messages: Sequence[PromptChatApiMessage]) -> list[SmarterJsonType]:
    """
    Messages as the prompt api's request sends them: only those that the LLM accepts.

    Smarter's own ``smarter`` and ``smarter_error`` messages are left out, as Smarter Chat leaves them out.
    Every message keeps its ``content``, even when it is null, e.g. an assistant's tool calls: the
    platform requires the key.

    :param messages: A chat thread.
    :returns: The messages, as JSON.
    """
    result: list[SmarterJsonType] = []
    for message in messages:
        if message.role not in LLM_MESSAGE_ROLES:
            continue
        data = message.model_dump(mode="json", exclude_none=True)
        data.setdefault("content", None)
        result.append(data)
    return result


class PromptStream:
    """
    A prompt whose progress is streamed as Server-Sent Events.

    Iterate it for the :class:`PromptChatApiProgressEvent` events, e.g. "Calling tool calculator". When
    the iteration ends, :attr:`response` is the prompt's response, exactly as a non-streaming prompt
    returns it. Use it as a context manager, so that the connection is closed.

    :param events: The context manager of the stream's Server-Sent Events.
    """

    def __init__(self, events: AbstractContextManager[Iterator[ServerSentEvent]]) -> None:
        self._events_cm = events
        self._events: Iterator[ServerSentEvent] | None = None
        self._result: PromptChatApiProgressResult | None = None

    def __enter__(self) -> PromptStream:
        self._events = self._events_cm.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._events_cm.__exit__(exc_type, exc, traceback)

    def __iter__(self) -> Iterator[PromptChatApiProgressEvent]:
        if self._events is None:
            self.__enter__()
        assert self._events is not None  # nosec B101 - set by __enter__
        for event in self._events:
            if event.event == "progress":
                yield PromptChatApiProgressEvent.model_validate(event.json())
            elif event.event == "result":
                self._result = PromptChatApiProgressResult.model_validate(event.json())

    def until_done(self) -> PromptChatApiPromptResponse:
        """
        Read the stream to its end, discarding the progress events.

        :returns: The prompt's response.
        """
        for _ in self:
            pass
        return self.response

    @property
    def result(self) -> PromptChatApiProgressResult | None:
        """The final ``result`` event, once the stream has been read: the prompt's status and response."""
        return self._result

    @property
    def response(self) -> PromptChatApiPromptResponse:
        """
        The prompt's response, once the stream has been read.

        :raises SmarterPromptError: If the prompt failed.
        :raises SmarterError: If the stream has not been read, or ended without a result.
        """
        if self._result is None:
            raise SmarterError("The stream has not been read to its end, or it ended without a result event.")
        response = self._result.response
        if isinstance(response, PromptChatApiErrorResponse):
            raise SmarterPromptError(response.error.description, response)
        if response.error is not None:
            raise SmarterPromptError(response.error.description, response)
        return response


class ChatSession:
    """
    A multi-turn conversation with an LLMClient.

    It keeps the chat session's key, so that the platform keeps the session's history, and the
    thread, which it sends with each prompt as Smarter Chat does. Create one with
    :meth:`LLMClients.chat`.

    :param llmclients: The LLMClients resource.
    :param llmclient_id: The LLMClient's id or hashed id.
    :param config: The chat session's configuration.
    """

    def __init__(self, llmclients: LLMClients, llmclient_id: SmarterIdType, config: PromptChatApiConfig) -> None:
        self._llmclients = llmclients
        self.llmclient_id = llmclient_id
        self.config = config
        self.messages: list[PromptChatApiMessage] = list(config.history.chat_history) or self._introduction(config)

    @staticmethod
    def _introduction(config: PromptChatApiConfig) -> list[PromptChatApiMessage]:
        """A new thread: the LLMClient's system prompt and welcome message, as Smarter Chat starts one."""
        messages = []
        if config.llmclient.default_system_role:
            messages.append(PromptChatApiMessage(role="system", content=config.llmclient.default_system_role))
        if config.llmclient.app_welcome_message:
            messages.append(PromptChatApiMessage(role="assistant", content=config.llmclient.app_welcome_message))
        return messages

    @property
    def session_key(self) -> str:
        """The chat session's key, with which the session can be resumed: see :meth:`LLMClients.chat`."""
        return self.config.session_key

    def send(self, content: str | MessageInput) -> PromptChatApiPromptResponse:
        """
        Send a message, and add it and the prompt's messages to the thread.

        :param content: A user message's text, or a message.
        :returns: The prompt's response. ``.text`` is the LLM's reply.
        """
        message = to_messages(content)[0] if isinstance(content, str) else to_messages([content])[0]
        thread = [*self.messages, message]
        response = self._llmclients.prompt(self.llmclient_id, thread, session_key=self.session_key)
        self.messages = [*thread, *response.data.messages]
        return response

    def stream(self, content: str | MessageInput) -> ChatStream:
        """
        Send a message, and stream the prompt's progress.

        The thread is updated when the stream has been read to its end.

        :param content: A user message's text, or a message.
        :returns: The stream. Use it as a context manager.
        """
        message = to_messages(content)[0] if isinstance(content, str) else to_messages([content])[0]
        thread = [*self.messages, message]
        events = self._llmclients._events(
            self.llmclient_id, thread, session_key=self.session_key
        )  # pylint: disable=protected-access
        return ChatStream(events, self, thread)


class ChatStream(PromptStream):
    """A :class:`PromptStream` of a :class:`ChatSession`, which adds the prompt's messages to the session's thread."""

    def __init__(
        self,
        events: AbstractContextManager[Iterator[ServerSentEvent]],
        session: ChatSession,
        thread: list[PromptChatApiMessage],
    ) -> None:
        super().__init__(events)
        self._session = session
        self._thread = thread

    def __iter__(self) -> Iterator[PromptChatApiProgressEvent]:
        yield from super().__iter__()
        response = self._result.response if self._result is not None else None
        if isinstance(response, PromptChatApiPromptResponse) and response.error is None:
            self._session.messages = [*self._thread, *self._result.response.data.messages]


class LLMClients(SmarterKindResource[LLMClient]):
    """LLMClients: ``/api/v1/llm-clients/``, and the manifest api's ``LLMClient`` kind."""

    kind = "LLMClient"
    path = "llm-clients/"
    model = LLMClient

    def config(
        self, id: SmarterIdType, *, session_key: str | None = None
    ) -> PromptChatApiConfig:  # pylint: disable=redefined-builtin
        """
        An LLMClient's chat configuration, and a chat session.

        :param id: The LLMClient's id or hashed id.
        :param session_key: An existing session's key, to resume it with its history, or None for a new session.
        :returns: The configuration, whose ``session_key`` identifies the session.
        """
        response = self._http.request(
            "POST",
            f"{self.path}{resource_id(id)}/config/",
            json={"session_key": session_key},
            cast_to=PromptChatApiConfigResponse,
        )
        return response.data

    def prompt(
        self,
        id: SmarterIdType,  # pylint: disable=redefined-builtin
        prompt: PromptInput,
        *,
        session_key: str | None = None,
        timeout: float | None = None,
    ) -> PromptChatApiPromptResponse:
        """
        Prompt an LLMClient.

        The platform runs the LLMClient's whole prompt: it selects plugins, calls the LLM, runs the
        tools that the LLM calls, and applies the Guardrails. Prompts are billed by the LLM provider.

        :param id: The LLMClient's id or hashed id.
        :param prompt: The text of one user message, or the chat thread as a list of messages.
        :param session_key: The chat session's key, from :meth:`config`, to keep the prompt's history
            in that session.
        :param timeout: Seconds, instead of the client's timeout.
        :returns: The response. ``.text`` is the LLM's final reply, and ``.data.messages`` every
            message that the prompt added, including Smarter's own.
        :raises APIStatusError: If the prompt failed, e.g. the LLM provider returned an error. The
            exception's ``body`` is the error response.
        """
        return self._http.request(
            "POST",
            f"{self.path}{resource_id(id)}/prompt/",
            json={"session_key": session_key, "messages": request_messages(to_messages(prompt))},
            cast_to=PromptChatApiPromptResponse,
            timeout=timeout,
        )

    def stream(
        self,
        id: SmarterIdType,  # pylint: disable=redefined-builtin
        prompt: PromptInput,
        *,
        session_key: str | None = None,
        timeout: float | None = None,
    ) -> PromptStream:
        """
        Prompt an LLMClient, and stream its progress: the LLM requests, tool calls and plugin calls.

        :param id: The LLMClient's id or hashed id.
        :param prompt: The text of one user message, or the chat thread as a list of messages.
        :param session_key: The chat session's key.
        :param timeout: Seconds to wait for each event, instead of the client's timeout.
        :returns: The stream. Use it as a context manager, and iterate it for the progress events.
        """
        return PromptStream(self._events(id, prompt, session_key=session_key, timeout=timeout))

    def _events(
        self,
        id: SmarterIdType,  # pylint: disable=redefined-builtin
        prompt: PromptInput,
        *,
        session_key: str | None = None,
        timeout: float | None = None,
    ) -> AbstractContextManager[Iterator[ServerSentEvent]]:
        """The Server-Sent Events of a prompt, which are requested when the context manager is entered."""
        return self._http.stream_events(
            "POST",
            f"{self.path}{resource_id(id)}/prompt/",
            json={"session_key": session_key, "messages": request_messages(to_messages(prompt))},
            timeout=timeout,
        )

    def chat(
        self, id: SmarterIdType, *, session_key: str | None = None
    ) -> ChatSession:  # pylint: disable=redefined-builtin
        """
        Start or resume a conversation with an LLMClient.

        :param id: The LLMClient's id or hashed id.
        :param session_key: An existing session's key, to resume it, or None for a new session.
        :returns: The chat session.
        """
        return ChatSession(self, id, self.config(id, session_key=session_key))

    def plugins(self, id: SmarterIdType) -> list[LLMClientPlugin]:  # pylint: disable=redefined-builtin
        """
        An LLMClient's plugins.

        :param id: The LLMClient's integer id.
        :returns: The plugins.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/plugins/", cast_to=list[LLMClientPlugin])

    def extensions(self, id: SmarterIdType) -> list[LLMClientExtension]:  # pylint: disable=redefined-builtin
        """
        The extensions whose tools an LLMClient offers the LLM, e.g. ``calculator``.

        :param id: The LLMClient's integer id.
        :returns: The extensions.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/extensions", cast_to=list[LLMClientExtension])

    def api_keys(self, id: SmarterIdType) -> list[LLMClientApiKey]:  # pylint: disable=redefined-builtin
        """
        The api keys that may call an LLMClient that requires authentication.

        :param id: The LLMClient's integer id.
        :returns: The api keys.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/apikeys/", cast_to=list[LLMClientApiKey])

    def custom_domains(self, id: SmarterIdType) -> list[LLMClientCustomDomain]:  # pylint: disable=redefined-builtin
        """
        The custom domains of an LLMClient.

        :param id: The LLMClient's integer id.
        :returns: The custom domains.
        """
        return self._http.request(
            "GET", f"{self.path}{resource_id(id)}/customdomains", cast_to=list[LLMClientCustomDomain]
        )

    def deploy(self, name: str) -> SmarterJournalMessage:
        """
        Deploy an LLMClient on its own host name.

        This creates real, possibly billable infrastructure: DNS records, a TLS certificate and a
        Kubernetes ingress.

        :param name: The LLMClient's name.
        :returns: The platform's response.
        """
        return self._client.manifests.deploy(self.kind, name)

    def undeploy(self, name: str) -> SmarterJournalMessage:
        """
        Undo an LLMClient's deployment.

        :param name: The LLMClient's name.
        :returns: The platform's response.
        """
        return self._client.manifests.undeploy(self.kind, name)


__all__ = [
    "ChatSession",
    "ChatStream",
    "LLMClients",
    "MessageInput",
    "PromptInput",
    "PromptStream",
    "SmarterPromptError",
    "request_messages",
    "to_messages",
]
