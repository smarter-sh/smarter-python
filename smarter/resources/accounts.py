"""
Accounts, their users, and their contacts: ``/api/v1/accounts/``, and each user's token usage and data exports.

Only superusers may read accounts, users and contacts: the platform refuses other users with a 403.
Every user may read their own token usage, and export their own data.

Users and accounts are created and changed with manifests (the ``User`` and ``Account`` kinds):
see :class:`smarter.resources.manifests.Manifests`.

.. code-block:: python

    for point in client.accounts.usage("7_days").points:
        print(point.period_start, point.total_tokens, point.total_cost)

    export = client.accounts.data_exports.start()   # a link to the zip file is emailed to the user
    print(client.accounts.data_exports.retrieve(export.id).status)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from smarter.core.typing import SmarterIdType
from smarter.models.account import Account, AccountContact, User, UserProfile
from smarter.models.usage import DataExport, DataExportOverview, TokenUsage

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


class UserProfiles(SmarterAPIResource):
    """Each user's membership of an account: ``/api/v1/accounts/user-profiles/``."""

    path = "accounts/user-profiles/"

    def list(self) -> list[UserProfile]:
        """
        The user profiles that the api key's user may read.

        :returns: The user profiles.
        """
        return self._http.request("GET", self.path, cast_to=list[UserProfile])

    def retrieve(self, id: SmarterIdType) -> UserProfile:  # pylint: disable=redefined-builtin
        """
        A user profile, by id.

        :param id: The user profile's id.
        :returns: The user profile.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/", cast_to=UserProfile)


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


class DataExports(SmarterAPIResource):
    """
    Download My Data: ``/api/v1/accounts/data-exports/``.

    An export is a zip file of the manifest of every resource that the api key's user owns, in every
    account they belong to, with Secrets' values redacted. The platform builds it in the background,
    and emails the user a link to it: the api never returns the link. Every user may export their own
    data, a few times a day.
    """

    path = "accounts/data-exports/"

    def overview(self) -> DataExportOverview:
        """
        What the user may export: the address that the link is emailed to, the limits, and their latest export.

        :returns: The overview.
        """
        return self._http.request("GET", self.path, cast_to=DataExportOverview)

    def start(self) -> DataExport:
        """
        Start an export of the user's data, unless one is in progress.

        The request is never retried, whatever the client's ``max_retries``: the platform refuses an
        export with a 429 that a retry would not change, and an export sends an email.

        :returns: The new export, or the one that is already in progress.
        :raises RateLimitError: If the user has no email address, or has started too many exports today.
            Its ``message`` says which.
        """
        return self._http.request("POST", self.path, cast_to=DataExport, max_retries=0)

    def retrieve(self, export_id: int) -> DataExport:
        """
        An export's progress.

        :param export_id: The export's id.
        :returns: The export.
        :raises NotFoundError: If the user has no such export.
        """
        return self._http.request("GET", f"{self.path}{resource_id(export_id)}/", cast_to=DataExport)


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
        self.user_profiles = UserProfiles(client)
        """The users' memberships of accounts."""
        self.data_exports = DataExports(client)
        """The user's exports of their own data."""

    def usage(
        self, periodicity: Literal["12_hours", "24_hours", "7_days", "1_month", "1_year"] = "24_hours"
    ) -> TokenUsage:
        """
        The tokens and cost of the api key's user's LLM requests over a window of time, oldest first.

        Every user may read their own. The platform caches it for five minutes.

        :param periodicity: The window, e.g. ``24_hours``, the current hour and the 23 before it, one
            point per hour. ``7_days`` and ``1_month`` have a point per day, and ``1_year`` per month.
        :returns: One point per period.
        :raises BadRequestError: If the platform does not know the periodicity.
        """
        return self._http.request("GET", f"{self.path}usage/", params={"periodicity": periodicity}, cast_to=TokenUsage)


__all__ = ["AccountContacts", "Accounts", "DataExports", "UserProfiles", "Users"]
