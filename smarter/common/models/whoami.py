# pylint: disable=C0115
"""
smarter.common.models.whoami
This module contains the WhoAmIModel class, which is used to represent the
response from the WhoAmI API endpoint. The WhoAmI API endpoint is used to
retrieve information about the current user and their account.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr

from smarter.common.models.base import MetadataModel, SmarterApiBaseModel


class UserModel(BaseModel):
    id: int
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: EmailStr
    is_staff: bool
    is_superuser: bool


class AccountModel(BaseModel):
    id: int
    created_at: str
    updated_at: str
    account_number: str
    is_default_account: bool
    company_name: str
    phone_number: str
    address1: str
    address2: Optional[str]
    city: str
    state: str
    postal_code: str
    country: str
    language: Optional[str]
    timezone: str
    currency: str


class WhoAmIModel(SmarterApiBaseModel):
    data: dict
    api: str
    thing: Optional[str]
    metadata: MetadataModel
    message: Optional[str] = None
    error: Optional[str] = None  # FIX ME: This should be a dict

    @property
    def user(self) -> UserModel:
        return UserModel(**self.data["user"])

    @property
    def account(self) -> AccountModel:
        return AccountModel(**self.data["account"])

    @property
    def environment(self) -> str:
        return self.data["environment"]
