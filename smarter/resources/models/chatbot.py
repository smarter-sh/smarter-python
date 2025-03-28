# pylint: disable=C0115
"""
smarter.resources.models.chatbot
This module contains the models for the Smarter API chatbot endpoint.
The models are used to represent the request and response data for the
chatbot API endpoint.
"""
from typing import Any, List, Optional

from pydantic import BaseModel

from smarter.common.models.base import SmarterApiBaseModel


class ConfigModel(BaseModel):
    subdomain: Optional[str] = None
    customDomain: Optional[str] = None
    deployed: bool
    provider: str
    defaultModel: str
    defaultSystemRole: str
    defaultTemperature: float
    defaultMaxTokens: int
    appName: Optional[str] = None
    appAssistant: Optional[str] = None
    appWelcomeMessage: Optional[str] = None
    appExamplePrompts: Optional[str] = None
    appPlaceholder: Optional[str] = None
    appInfoUrl: Optional[str] = None
    appBackgroundImageUrl: Optional[str] = None
    appLogoUrl: Optional[str] = None
    appFileAttachment: Optional[str] = None
    dnsVerificationStatus: str
    tlsCertificateIssuanceStatus: str


class SpecModel(BaseModel):
    config: ConfigModel
    plugins: List[Any] = []
    functions: List[Any] = []
    apiKey: Optional[str] = None


class StatusModel(BaseModel):
    created: str
    modified: str
    deployed: bool
    defaultHost: str
    defaultUrl: str
    customUrl: Optional[str] = None
    sandboxHost: str
    sandboxUrl: str
    hostname: str
    scheme: str
    url: str
    urlChatbot: str
    urlChatapp: str
    dnsVerificationStatus: str


class MetadataModel(BaseModel):
    name: str
    description: str
    version: str


class DataModel(BaseModel):
    apiVersion: str
    kind: str
    metadata: MetadataModel
    spec: SpecModel
    status: StatusModel


class ChatbotModel(SmarterApiBaseModel):
    data: DataModel
