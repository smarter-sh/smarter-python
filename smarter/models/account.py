"""Models of accounts, users, user profiles and account contacts, as ``/api/v1/accounts/`` returns them."""

from datetime import datetime
from typing import Optional

from .base import SmarterAccountRef, SmarterCamelModel, SmarterResource


class Account(SmarterResource):
    """A Smarter account: the tenant that owns users and resources."""

    account_number: str
    is_default_account: Optional[bool] = None
    company_name: Optional[str] = None
    phone_number: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None


class User(SmarterCamelModel):
    """A user of the platform."""

    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_staff: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserProfile(SmarterResource):
    """A user's membership of an account, which owns the resources that the user creates in it."""

    user: User
    account: SmarterAccountRef
    profile_image_url: Optional[str] = None
    is_test: Optional[bool] = None


class AccountContact(SmarterCamelModel):
    """A contact of an account, who receives its notices."""

    id: int
    account: Optional[SmarterAccountRef] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_primary: Optional[bool] = None
    is_test: Optional[bool] = None
    welcomed: Optional[bool] = None


__all__ = ["Account", "AccountContact", "User", "UserProfile"]
