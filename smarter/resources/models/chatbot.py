# pylint: disable=C0115
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Config(BaseModel):
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


class Spec(BaseModel):
    config: Config
    plugins: List[Any] = []
    functions: List[Any] = []
    apiKey: Optional[str] = None


class Status(BaseModel):
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


class Metadata(BaseModel):
    name: str
    description: str
    version: str


class Data(BaseModel):
    apiVersion: str
    kind: str
    metadata: Metadata
    spec: Spec
    status: Status


class ChatbotModel(BaseModel):
    data: Data
    message: str
    api: str
    thing: str
    metadata: Dict[str, str]
