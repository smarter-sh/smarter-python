# pylint: disable=C0115
"""
smarter.resources.models.prompt
This module contains the models for the Smarter API prompt endpoint.
The models are used to represent the request and response data for the
prompt API endpoint.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Annotation(BaseModel):
    pass  # Placeholder for annotations if they have a specific structure


class MessageModel(BaseModel):
    role: str
    content: str
    refusal: Optional[Any] = None
    audio: Optional[Any] = None
    function_call: Optional[Any] = None
    tool_calls: Optional[Any] = None
    annotations: Optional[List[Annotation]] = []


class ChoiceModel(BaseModel):
    finish_reason: str
    index: int
    logprobs: Optional[Any] = None
    message: MessageModel


class CompletionTokensDetailsModel(BaseModel):
    accepted_prediction_tokens: int
    audio_tokens: int
    reasoning_tokens: int
    rejected_prediction_tokens: int


class PromptTokensDetailsModel(BaseModel):
    audio_tokens: int
    cached_tokens: int


class UsageModel(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_tokens_details: CompletionTokensDetailsModel
    prompt_tokens_details: PromptTokensDetailsModel


class MetadataModel(BaseModel):
    tool_calls: Optional[Any] = None
    model: str
    temperature: float
    max_tokens: int
    input_text: str


class SmarterIterationRequestModel(BaseModel):
    model: str
    messages: List[MessageModel]
    tools: List[Dict[str, Any]]
    temperature: float
    max_tokens: int
    tool_choice: str


class SmarterIterationResponseModel(BaseModel):
    id: str
    choices: List[ChoiceModel]
    created: int
    model: str
    object: str
    service_tier: str
    system_fingerprint: str
    usage: UsageModel
    metadata: MetadataModel


class SmarterFirstIterationModel(BaseModel):
    request: SmarterIterationRequestModel
    response: SmarterIterationResponseModel


class SmarterModel(BaseModel):
    first_iteration: SmarterFirstIterationModel
    second_iteration: Optional[Dict[str, Any]] = {}
    tools: List[str]
    plugins: List[Any]
    messages: List[MessageModel]


class BodyModel(BaseModel):
    id: str
    choices: List[ChoiceModel]
    created: int
    model: str
    object: str
    service_tier: str
    system_fingerprint: str
    usage: UsageModel
    metadata: MetadataModel
    smarter: SmarterModel


class ResponseDataModel(BaseModel):
    isBase64Encoded: bool = Field(default=False)
    statusCode: int
    headers: Dict[str, str]
    body: BodyModel


class ResponseModel(BaseModel):
    data: ResponseDataModel


class RequestModel(BaseModel):
    session_key: str
    messages: List[MessageModel]


class DataModel(BaseModel):
    request: RequestModel
    response: ResponseModel


class PromptResponseModel(BaseModel):
    data: DataModel
    api: str
    thing: str
