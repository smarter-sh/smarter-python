# pylint: disable=C0115
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Annotation(BaseModel):
    pass  # Placeholder for annotations if they have a specific structure


class Message(BaseModel):
    role: str
    content: str
    refusal: Optional[Any] = None
    audio: Optional[Any] = None
    function_call: Optional[Any] = None
    tool_calls: Optional[Any] = None
    annotations: Optional[List[Annotation]] = []


class Choice(BaseModel):
    finish_reason: str
    index: int
    logprobs: Optional[Any] = None
    message: Message


class CompletionTokensDetails(BaseModel):
    accepted_prediction_tokens: int
    audio_tokens: int
    reasoning_tokens: int
    rejected_prediction_tokens: int


class PromptTokensDetails(BaseModel):
    audio_tokens: int
    cached_tokens: int


class Usage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_tokens_details: CompletionTokensDetails
    prompt_tokens_details: PromptTokensDetails


class Metadata(BaseModel):
    tool_calls: Optional[Any] = None
    model: str
    temperature: float
    max_tokens: int
    input_text: str


class SmarterIterationRequest(BaseModel):
    model: str
    messages: List[Message]
    tools: List[Dict[str, Any]]
    temperature: float
    max_tokens: int
    tool_choice: str


class SmarterIterationResponse(BaseModel):
    id: str
    choices: List[Choice]
    created: int
    model: str
    object: str
    service_tier: str
    system_fingerprint: str
    usage: Usage
    metadata: Metadata


class SmarterFirstIteration(BaseModel):
    request: SmarterIterationRequest
    response: SmarterIterationResponse


class Smarter(BaseModel):
    first_iteration: SmarterFirstIteration
    second_iteration: Optional[Dict[str, Any]] = {}
    tools: List[str]
    plugins: List[Any]
    messages: List[Message]


class Body(BaseModel):
    id: str
    choices: List[Choice]
    created: int
    model: str
    object: str
    service_tier: str
    system_fingerprint: str
    usage: Usage
    metadata: Metadata
    smarter: Smarter


class ResponseData(BaseModel):
    isBase64Encoded: bool = Field(default=False)
    statusCode: int
    headers: Dict[str, str]
    body: Body


class Response(BaseModel):
    data: ResponseData


class Request(BaseModel):
    session_key: str
    messages: List[Message]


class Data(BaseModel):
    request: Request
    response: Response


class PromptResponseModel(BaseModel):
    data: Data
    api: str
    thing: str
