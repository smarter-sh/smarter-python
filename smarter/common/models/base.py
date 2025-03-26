# pylint: disable=C0115
"""
Base models for all API responses.
"""
from typing import Optional

from pydantic import BaseModel


class MetadataModel(BaseModel):
    """
    Metadata model for all API responses. Key might vary depending on the API end points.
    Not sure how to handle that yet.
    """

    key: str


class SmarterApiBaseModel(BaseModel):
    """
    Base model for all API responses. 'data' and 'status' will vary for each
    API end point and are assumed to be overridden by the inheriting class.
    """

    data: dict
    api: str
    thing: Optional[str]
    metadata: MetadataModel
    status: dict = None
    message: Optional[str] = None
    error: Optional[str] = None  # FIX ME: This should be a dict
