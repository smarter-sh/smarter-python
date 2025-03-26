# pylint: disable=C0115
from typing import Optional

from pydantic import BaseModel, EmailStr


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


class MetadataModel(BaseModel):
    key: str


class WhoAmIModel(BaseModel):
    data: dict
    user: UserModel
    account: AccountModel
    environment: str
    api: str
    thing: Optional[str]
    metadata: MetadataModel
