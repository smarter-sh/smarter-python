"""
Accounts, their users, and their contacts: ``/api/v1/accounts/``.

Users and accounts are created and changed with manifests (the ``User`` and ``Account`` kinds):
see :class:`smarter.resources.manifests.Manifests`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from smarter.core.typing import SmarterIdType
from smarter.models.account import Account, AccountContact, User

from .base import SmarterAPIResource, SmarterKindResource, resource_id

if TYPE_CHECKING:
    from smarter.client import Smarter


class Users(SmarterAPIResource):
    """The users of the api key's account: ``/api/v1/accounts/users/``."""

    path = "accounts/users/"

    def list(self) -> list[User]:
        """
        The users that the api key's user may read.

        :returns: The users.
        """
        return self._http.request("GET", self.path, cast_to=list[User])

    def retrieve(self, id: SmarterIdType) -> User:  # pylint: disable=redefined-builtin
        """
        A user, by id.

        :param id: The user's id.
        :returns: The user.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/", cast_to=User)


class AccountContacts(SmarterAPIResource):
    """The contacts of the api key's account: ``/api/v1/accounts/contacts/``."""

    path = "accounts/contacts/"

    def list(self) -> list[AccountContact]:
        """
        The account's contacts.

        :returns: The contacts.
        """
        return self._http.request("GET", self.path, cast_to=list[AccountContact])

    def retrieve(self, id: SmarterIdType) -> AccountContact:  # pylint: disable=redefined-builtin
        """
        A contact, by id.

        :param id: The contact's id.
        :returns: The contact.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/", cast_to=AccountContact)


class Accounts(SmarterKindResource[Account]):
    """Accounts: ``/api/v1/accounts/``, and the manifest api's ``Account`` kind."""

    kind = "Account"
    path = "accounts/"
    model = Account

    def __init__(self, client: Smarter) -> None:
        super().__init__(client)
        self.users = Users(client)
        """The account's users."""
        self.contacts = AccountContacts(client)
        """The account's contacts."""


__all__ = ["AccountContacts", "Accounts", "Users"]
