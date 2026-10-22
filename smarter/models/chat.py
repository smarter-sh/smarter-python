"""
Models of the Smarter Chat api contract, version 2: an LLMClient's configuration, its prompt api's request and response, and the prompt's progress events.

These mirror ``smarter.apps.prompt.contract.models`` in the Smarter platform, whose JSON Schema is
``chat-contract.schema.json``. The SDK always asks for version 2 of the contract (with the
``X-Smarter-Capabilities: chat-contract-v2`` request header), so the deprecated version 1 models are
not mirrored.

Two deliberate differences from the platform's models, both so that an SDK keeps working when the
platform is upgraded:

- every model allows extra fields, including the models of Django rows, whose platform models forbid
  them, and
- values that the platform may add to, such as a plugin's class or a progress event's type, are
  ``str`` rather than ``Literal``. Their known values are listed in the field descriptions.

The SDK's tests validate the platform's published example of every contract model against these
models. See ``scripts/sync-contracts.sh``.
"""

from datetime import datetime
from typing import Annotated, Literal, Optional, Union

from pydantic import Field

from smarter.core.typing import SmarterJsonObjectType, SmarterJsonType

from .base import SmarterModel

CHAT_CONTRACT_V2 = 2
"""The version of the Smarter Chat api contract that the SDK reads."""

CHAT_CONTRACT_V2_CAPABILITY = "chat-contract-v2"
"""The ``X-Smarter-Capabilities`` value with which the SDK asks for version 2 of the contract."""

LLM_MESSAGE_ROLES = ("system", "assistant", "user", "tool")
"""The message roles that the LLM providers accept.

Smarter's own roles, ``smarter`` and ``smarter_error``, are informational.
"""


# ------------------------------------------------------------------------------
# messages
# ------------------------------------------------------------------------------


class PromptChatApiTextPart(SmarterModel):
    """A text part of a message's content."""

    type: Literal["text"]
    text: str


class PromptChatApiImageUrl(SmarterModel):
    """An image, by its url or as a data url."""

    url: str
    detail: Optional[Literal["auto", "low", "high"]] = None


class PromptChatApiImagePart(SmarterModel):
    """An image part of a message's content."""

    type: Literal["image_url"]
    image_url: PromptChatApiImageUrl


class PromptChatApiInputAudio(SmarterModel):
    """Audio, base64 encoded."""

    data: str
    format: Literal["wav", "mp3"]


class PromptChatApiAudioPart(SmarterModel):
    """An audio part of a message's content."""

    type: Literal["input_audio"]
    input_audio: PromptChatApiInputAudio


class PromptChatApiFileRef(SmarterModel):
    """A file, base64 encoded, or by the provider's file id."""

    file_data: Optional[str] = None
    file_id: Optional[str] = None
    filename: Optional[str] = None


class PromptChatApiFilePart(SmarterModel):
    """A file part of a message's content."""

    type: Literal["file"]
    file: PromptChatApiFileRef


class PromptChatApiRefusalPart(SmarterModel):
    """The LLM's refusal, as a part of a message's content."""

    type: Literal["refusal"]
    refusal: str


PromptChatApiContentPart = Annotated[
    Union[
        PromptChatApiTextPart,
        PromptChatApiImagePart,
        PromptChatApiAudioPart,
        PromptChatApiFilePart,
        PromptChatApiRefusalPart,
    ],
    Field(discriminator="type"),
]
"""A part of a message whose content is a list of parts, by its ``type``."""


class PromptChatApiFunctionCall(SmarterModel):
    """The function that a tool call calls."""

    name: str
    arguments: str = Field(..., description="The function's arguments, as a JSON string.")


class PromptChatApiToolCall(SmarterModel):
    """A tool call of an assistant message."""

    id: str
    type: str = "function"
    function: PromptChatApiFunctionCall


class PromptChatApiMessage(SmarterModel):
    """
    A message of a chat thread, in the format of the OpenAI api.

    Smarter adds its own roles: ``smarter`` for informational messages (e.g. the prompt's
    configuration, the tools presented to the LLM, and its token charges), and ``smarter_error``.
    These are saved in the session's history, and are never sent to the LLM.
    """

    role: str = Field(..., description="system, assistant, user, tool, smarter or smarter_error.")
    content: Optional[Union[str, list[PromptChatApiContentPart]]] = Field(
        None, description="The message's text, or a list of content parts."
    )
    tool_calls: Optional[list[PromptChatApiToolCall]] = Field(None, description="An assistant message's tool calls.")
    tool_call_id: Optional[str] = Field(None, description="The tool call that a tool message answers.")
    name: Optional[str] = Field(None, description="The name of a tool message's function.")

    @property
    def text(self) -> str:
        """The message's text: its content, or the text of its text parts, joined by blank lines."""
        if isinstance(self.content, str):
            return self.content
        if not self.content:
            return ""
        return "\n\n".join(part.text for part in self.content if isinstance(part, PromptChatApiTextPart))


class PromptChatApiJournalMetadata(SmarterModel):
    """The ``metadata`` of a chat response."""

    command: Optional[str] = Field(None, description="The journal's command, e.g. prompt.")
    thing: Optional[str] = Field(None, description="The journal's thing, e.g. LLMClient.")
    key: Optional[str] = None


class PromptChatApiErrorBody(SmarterModel):
    """The ``error`` of a chat error response."""

    errorClass: str = Field(..., description="The name of the error's class, e.g. NotFound or LLMProviderError.")
    description: str = Field(..., description="A human-readable description.")
    status: int = Field(..., description="The http status.")


class PromptChatApiErrorResponse(SmarterModel):
    """A chat error response."""

    error: PromptChatApiErrorBody
    api: Optional[str] = None
    metadata: Optional[PromptChatApiJournalMetadata] = None


class PromptChatApiEnvelope(SmarterModel):
    """The fields that every chat response adds beside ``data``."""

    api: str = Field(..., description='The api version, e.g. "smarter.sh/v1".')
    metadata: PromptChatApiJournalMetadata = Field(default_factory=PromptChatApiJournalMetadata)


# ------------------------------------------------------------------------------
# the configuration api
# ------------------------------------------------------------------------------


class PromptChatApiStyleSection(SmarterModel):
    """The colors of one section of the chat ui."""

    background_color: Optional[str] = None
    color: Optional[str] = None
    border_color: Optional[str] = None
    info_color: Optional[str] = None
    link_color: Optional[str] = None
    editor_background_color: Optional[str] = None
    placeholder_color: Optional[str] = None


class PromptChatApiStyles(SmarterModel):
    """The LLMClient's chat ui styles."""

    app_logo_url: Optional[str] = None
    app_background_image_url: Optional[str] = None
    app_background_image_size: Optional[str] = None
    assistant_avatar_url: Optional[str] = None
    user_avatar_url: Optional[str] = None
    font_family: Optional[str] = None
    google_font: Optional[str] = None
    font_size: Optional[str] = None
    border_radius: Optional[str] = None
    main_container: Optional[PromptChatApiStyleSection] = None
    conversation_header: Optional[PromptChatApiStyleSection] = None
    message_list: Optional[PromptChatApiStyleSection] = None
    incoming_message: Optional[PromptChatApiStyleSection] = None
    outgoing_message: Optional[PromptChatApiStyleSection] = None
    message_input: Optional[PromptChatApiStyleSection] = None
    buttons: Optional[PromptChatApiStyleSection] = None
    typing_indicator: Optional[PromptChatApiStyleSection] = None


class PromptChatApiLLMClient(SmarterModel):
    """The LLMClient, as its configuration describes it."""

    id: int
    name: str
    url_llmclient: Optional[str] = Field(None, description="The url of the LLMClient's prompt api.")
    version: Optional[str] = None
    deployed: Optional[bool] = None
    provider: Optional[str] = None
    default_model: Optional[str] = None
    default_system_role: Optional[str] = Field(None, description="The system prompt of a new chat session.")
    app_name: Optional[str] = None
    app_assistant: Optional[str] = None
    app_welcome_message: Optional[str] = None
    app_example_prompts: Optional[list[str]] = None
    app_placeholder: Optional[str] = None
    app_info_url: Optional[str] = None
    app_file_attachment: Optional[bool] = None
    styles: Optional[PromptChatApiStyles] = None
    total_tools: Optional[int] = Field(
        None, description="The number of the LLMClient's extensions, plugins and MCPClients."
    )


class PromptChatApiOrmModel(SmarterModel):
    """The fields of a Django row that the contract returns."""

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PromptChatApiPluginMeta(PromptChatApiOrmModel):
    """A plugin's metadata."""

    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    tags: list[str] = []
    annotations: Optional[Union[list[SmarterJsonObjectType], SmarterJsonObjectType]] = None
    plugin_class: str = Field(..., description="api, skill, sql, static, websearch or imagesearch.")


class PromptChatApiLLMClientPlugin(PromptChatApiOrmModel):
    """A plugin of the LLMClient."""

    llmclient: int
    plugin_meta: PromptChatApiPluginMeta


class PromptChatApiLLMClientExtension(PromptChatApiOrmModel):
    """An extension of the LLMClient, whose tools it offers the LLM."""

    llmclient: int
    extension: int = Field(..., description="The Extension's id.")
    name: str = Field(..., description="The Extension's slug, e.g. weather.")
    version: Optional[str] = Field(None, description="The Extension's installed version, e.g. 1.0.0.")
    enabled: bool = Field(..., description="Whether the Extension is enabled, so that its tools are offered.")


class PromptChatApiPromptRequest(SmarterModel):
    """The prompt api's request body."""

    session_key: Optional[str] = None
    messages: list[PromptChatApiMessage]


class PromptChatApiLLMClientRequest(PromptChatApiOrmModel):
    """A request that Smarter sent to the LLM."""

    llmclient: int
    request: Optional[PromptChatApiPromptRequest] = None
    session_key: Optional[str] = None
    is_aggregation: Optional[bool] = None


class PromptChatApiPromptToolCall(PromptChatApiOrmModel):
    """A tool call of the chat session."""

    prompt: int
    plugin: Optional[int] = None
    function_name: Optional[str] = None
    function_args: Optional[str] = None
    request: SmarterJsonType = None
    response: SmarterJsonType = None


class PromptChatApiPromptPluginUsage(PromptChatApiOrmModel):
    """A use of a plugin in the chat session."""

    prompt: int
    plugin: int
    input_text: Optional[str] = None


class PromptChatApiPluginSelection(PromptChatApiOrmModel):
    """A plugin selector's decision in the chat session."""

    plugin_selector: int
    search_term: Optional[str] = None
    messages: Optional[list[PromptChatApiMessage]] = None
    session_key: Optional[str] = None


class PromptChatApiHistory(SmarterModel):
    """
    The chat session's history.

    ``prompt_tool_call_history`` is returned only in the complete configuration, with ``verbose=True``.
    """

    chat_history: list[PromptChatApiMessage] = Field(
        default_factory=list, description="The session's messages, which restore the chat thread."
    )
    prompt_tool_call_history: Optional[list[PromptChatApiPromptToolCall]] = None
    prompt_plugin_usage_history: Optional[list[PromptChatApiPromptPluginUsage]] = None
    plugin_selector_history: Optional[list[PromptChatApiPluginSelection]] = None
    llmclient_request_history: Optional[list[PromptChatApiLLMClientRequest]] = None


class PromptChatApiMetaData(SmarterModel):
    """
    The LLMClient's state.

    The complete configuration, from :meth:`~smarter.resources.llmclients.LLMClients.config` with
    ``verbose=True``, adds the platform's other details of the LLMClient, which this model accepts as extra fields.
    """

    ready: Optional[bool] = None
    is_valid: Optional[bool] = None
    is_deployed: Optional[bool] = None
    is_authentication_required: Optional[bool] = Field(
        None, description="True if the LLMClient requires a Smarter api key, or a logged-in user."
    )
    is_custom_domain: Optional[bool] = Field(None, description="True if the request's host is a custom domain.")


class PromptChatApiListMetaData(SmarterModel):
    """The counts of a list of the LLMClient's plugins or extensions."""

    total_plugins: Optional[int] = None
    plugins_returned: Optional[int] = None
    total_extensions: Optional[int] = None
    extensions_returned: Optional[int] = None


class PromptChatApiPluginList(SmarterModel):
    """
    The LLMClient's plugins.

    The list itself is returned only in the complete configuration, with ``verbose=True``. Otherwise
    ``plugins`` is empty, and ``meta_data`` has the counts.
    """

    meta_data: PromptChatApiListMetaData
    plugins: list[PromptChatApiLLMClientPlugin] = Field(default_factory=list)


class PromptChatApiExtensionList(SmarterModel):
    """
    The LLMClient's extensions.

    The list itself is returned only in the complete configuration, with ``verbose=True``. Otherwise
    ``extensions`` is empty, and ``meta_data`` has the counts.
    """

    meta_data: PromptChatApiListMetaData
    extensions: list[PromptChatApiLLMClientExtension] = Field(default_factory=list)


class PromptChatApiConfig(SmarterModel):
    """
    An LLMClient's chat configuration: the LLMClient, the chat session's key and history, and its plugins and extensions.

    A new session's configuration has an empty history. Pass its ``session_key`` to the prompt api
    to continue the session.
    """

    contract: int = CHAT_CONTRACT_V2
    session_key: str = Field(..., description="The chat session's key.")
    sandbox_mode: bool = Field(..., description="True for a workbench url.")
    debug_mode: bool = Field(..., description="The platform's ENABLE_REACTAPP_DEBUG_MODE waffle switch.")
    meta_data: PromptChatApiMetaData
    llmclient: PromptChatApiLLMClient
    history: PromptChatApiHistory
    plugins: PromptChatApiPluginList
    extensions: Optional[PromptChatApiExtensionList] = None


class PromptChatApiConfigRequest(SmarterModel):
    """The configuration api's request body."""

    session_key: Optional[str] = Field(None, description="The chat session's key, or None for a new session.")


class PromptChatApiConfigResponse(PromptChatApiEnvelope):
    """The configuration api's response."""

    data: PromptChatApiConfig


# ------------------------------------------------------------------------------
# the prompt api
# ------------------------------------------------------------------------------


class PromptChatApiChoice(SmarterModel):
    """A choice of a chat completion."""

    index: int = 0
    finish_reason: Optional[str] = Field(None, description="e.g. stop, length or tool_calls.")
    message: Optional[PromptChatApiMessage] = None


class PromptChatApiTokenDetails(SmarterModel):
    """The breakdown of a completion's tokens."""

    reasoning_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None
    audio_tokens: Optional[int] = None


class PromptChatApiUsage(SmarterModel):
    """A chat completion's token usage."""

    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    prompt_tokens_details: Optional[PromptChatApiTokenDetails] = None
    completion_tokens_details: Optional[PromptChatApiTokenDetails] = None


class PromptChatApiCompletion(SmarterModel):
    """The LLM's chat completion, in the format of the OpenAI api."""

    id: Optional[str] = None
    object: Optional[str] = None
    created: Optional[int] = None
    model: Optional[str] = None
    choices: list[PromptChatApiChoice] = Field(default_factory=list)
    usage: Optional[PromptChatApiUsage] = None
    system_fingerprint: Optional[str] = None
    service_tier: Optional[str] = None


class PromptChatApiPromptResult(SmarterModel):
    """The result of a prompt."""

    contract: int = CHAT_CONTRACT_V2
    status: int = Field(..., description="The prompt's http status: 200, or the LLM provider's error status.")
    messages: list[PromptChatApiMessage] = Field(
        default_factory=list, description="The messages that the prompt added to the chat thread, in order."
    )
    completion: Optional[PromptChatApiCompletion] = Field(None, description="The LLM's chat completion.")
    plugins: list[str] = Field(default_factory=list, description="The plugins that Smarter selected.")
    tools: list[str] = Field(default_factory=list, description="The functions that the LLM could call.")

    @property
    def assistant_messages(self) -> list[PromptChatApiMessage]:
        """The assistant messages that the prompt added, which are the LLM's replies and tool calls."""
        return [message for message in self.messages if message.role == "assistant"]

    @property
    def text(self) -> str:
        """The text of the LLM's final reply: the last assistant message that has content, or an empty string."""
        for message in reversed(self.assistant_messages):
            if message.text:
                return message.text
        return ""


class PromptChatApiPromptResponse(PromptChatApiEnvelope):
    """
    The prompt api's response.

    A failed prompt has ``error`` too, and its ``data.messages`` include a ``smarter_error`` message.
    """

    data: PromptChatApiPromptResult
    error: Optional[PromptChatApiErrorBody] = None

    @property
    def text(self) -> str:
        """The text of the LLM's final reply.

        See :attr:`PromptChatApiPromptResult.text`.
        """
        return self.data.text


# ------------------------------------------------------------------------------
# the prompt's Server-Sent Events
# ------------------------------------------------------------------------------


class PromptChatApiProgressEvent(SmarterModel):
    """
    The data of a ``progress`` event: a step of a running prompt.

    Events may carry more fields, depending on their type, e.g. ``tool`` and ``arguments``.
    """

    type: str = Field(
        ...,
        description=(
            "llm_request, tool_requested, tool_responded, plugin_called, mcp_tool_called, "
            "mcp_tool_responded or mcp_tool_failed."
        ),
    )
    message: str = Field(..., description="A short sentence, which a chat ui can display as is.")


class PromptChatApiProgressResult(SmarterModel):
    """The data of the final ``result`` event."""

    status: int = Field(..., description="The prompt's http status.")
    response: Union[PromptChatApiPromptResponse, PromptChatApiErrorResponse] = Field(
        ..., description="Exactly the JSON of a non-streaming response."
    )


__all__ = [
    "CHAT_CONTRACT_V2",
    "CHAT_CONTRACT_V2_CAPABILITY",
    "LLM_MESSAGE_ROLES",
    "PromptChatApiAudioPart",
    "PromptChatApiChoice",
    "PromptChatApiCompletion",
    "PromptChatApiConfig",
    "PromptChatApiConfigRequest",
    "PromptChatApiConfigResponse",
    "PromptChatApiContentPart",
    "PromptChatApiEnvelope",
    "PromptChatApiErrorBody",
    "PromptChatApiErrorResponse",
    "PromptChatApiExtensionList",
    "PromptChatApiFileRef",
    "PromptChatApiFilePart",
    "PromptChatApiFunctionCall",
    "PromptChatApiHistory",
    "PromptChatApiImagePart",
    "PromptChatApiImageUrl",
    "PromptChatApiInputAudio",
    "PromptChatApiJournalMetadata",
    "PromptChatApiLLMClient",
    "PromptChatApiLLMClientExtension",
    "PromptChatApiLLMClientPlugin",
    "PromptChatApiLLMClientRequest",
    "PromptChatApiListMetaData",
    "PromptChatApiMessage",
    "PromptChatApiMetaData",
    "PromptChatApiOrmModel",
    "PromptChatApiPluginList",
    "PromptChatApiPluginMeta",
    "PromptChatApiPluginSelection",
    "PromptChatApiProgressEvent",
    "PromptChatApiProgressResult",
    "PromptChatApiPromptPluginUsage",
    "PromptChatApiPromptRequest",
    "PromptChatApiPromptResponse",
    "PromptChatApiPromptResult",
    "PromptChatApiPromptToolCall",
    "PromptChatApiRefusalPart",
    "PromptChatApiStyleSection",
    "PromptChatApiStyles",
    "PromptChatApiTextPart",
    "PromptChatApiTokenDetails",
    "PromptChatApiToolCall",
    "PromptChatApiUsage",
]
