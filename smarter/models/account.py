"""Models of accounts, users, user profiles and account contacts, as ``/api/v1/accounts/`` returns them."""

from datetime import datetime

from pydantic import Field

from .base import SmarterAccountRef, SmarterCamelModel, SmarterResource


class Account(SmarterResource):
    """A Smarter account: the tenant that owns users and resources."""

    account_number: str
    is_default_account: bool | None = None
    company_name: str | None = None
    phone_number: str | None = None
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    language: str | None = None
    timezone: str | None = None
    currency: str | None = None
    is_active: bool | None = None


class User(SmarterCamelModel):
    """A user of the platform."""

    id: int
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    is_staff: bool | None = None
    is_superuser: bool | None = None


class UserProfile(SmarterResource):
    """A user's membership of an account, which owns the resources that the user creates in it."""

    user: User
    account: SmarterAccountRef
    profile_image: str | None = Field(
        None, description="The url of the image that the user uploaded, which takes precedence over profile_image_url."
    )
    profile_image_url: str | None = Field(None, description="The url of the image that the oauth provider supplied.")
    is_test: bool | None = None


class AccountContact(SmarterCamelModel):
    """A contact of an account, who receives its notices."""

    id: int
    account: SmarterAccountRef | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    is_primary: bool | None = None
    is_test: bool | None = None
    welcomed: bool | None = None


__all__ = ["Account", "AccountContact", "User", "UserProfile"]
