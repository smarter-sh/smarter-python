"""
Extensions: packages of LLM tools that a superuser installs on the platform, and LLMClients use.

An extension comes from the Smarter extension registry, or from an uploaded .zip archive. It is
installed disabled: configure its settings, then enable it. Every user may read the extensions that
their account may use; only superusers may install and manage them (the platform answers 403 to
anyone else).

.. code-block:: python

    for extension in client.extensions.list().objects:
        print(extension.slug, extension.installed_version, extension.enabled)

    client.extensions.install("weather")
    client.extensions.configure("weather", secrets={"google_maps_api_key": "AIza..."})
    client.extensions.enable("weather")
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import IO, Union

from smarter.core.typing import SmarterJsonObjectType, SmarterJsonType
from smarter.models.extension import (
    ExtensionActionResult,
    ExtensionDetail,
    ExtensionDetailResponse,
    ExtensionList,
    ExtensionRegistry,
    ExtensionSettingValue,
)

from .base import SmarterAPIResource, resource_id

ExtensionArchive = Union[str, Path, IO[bytes]]
"""An extension's .zip archive: its path, or a binary file object open for reading."""

ExtensionSecretValue = Union[str, int, None]
"""A secret setting's new value.

A string to save in a new Secret, the id of one of the platform admin's Secrets, or None to clear it.
"""


class Extensions(SmarterAPIResource):
    """
    The platform's extensions: ``/api/v1/extensions/``.

    Not to be confused with the extensions of one LLMClient, which
    :meth:`~smarter.resources.llmclients.LLMClients.extensions` lists.
    """

    path = "extensions/"

    def list(self) -> ExtensionList:
        """
        The installed extensions that the user may see, by display name.

        A user who is not a superuser sees only the extensions that their account may use.

        :returns: The extensions, whether the registry is enabled, and how many updates it has.
        """
        return self._http.request("GET", self.path, cast_to=ExtensionList)

    def registry(self, *, refresh: bool = False) -> ExtensionRegistry:
        """
        The registry's extensions, with what each offers this platform: install, update, or nothing, and why.

        :param refresh: True to download the registry's index again, rather than read the platform's
            cache. Superusers only.
        :returns: The registry's extensions, or why it cannot be read.
        """
        return self._http.request(
            "GET", f"{self.path}registry/", params={"refresh": refresh or None}, cast_to=ExtensionRegistry
        )

    def retrieve(self, slug: str) -> ExtensionDetail:
        """
        An installed extension: its documentation, tools, settings, versions, resources, switches and availability.

        A user who is not a superuser gets it without its settings, the accounts that may use it,
        the platform admin's Secrets, or who installed each version.

        :param slug: The extension's slug, e.g. ``weather``.
        :returns: The extension.
        :raises NotFoundError: If it is not installed, or the user's account may not use it.
        """
        response = self._http.request("GET", f"{self.path}{resource_id(slug)}/", cast_to=ExtensionDetailResponse)
        return response.extension

    def check_updates(self) -> ExtensionActionResult:
        """
        Download the registry's index, and record each installed extension's newest compatible version.

        Superusers only.

        :returns: A message that names the available updates. Its ``extension`` is None.
        :raises PermissionDeniedError: If the user is not a superuser.
        """
        return self._http.request("POST", f"{self.path}check-updates/", cast_to=ExtensionActionResult)

    def install(self, slug: str, version: str | None = None) -> ExtensionActionResult:
        """
        Install, or update, an extension from the registry.

        Superusers only. It is installed disabled: configure its settings, then enable it.

        :param slug: The extension's slug, e.g. ``weather``.
        :param version: The version, or None for the newest compatible version.
        :returns: A message, and the installed extension.
        :raises PermissionDeniedError: If the user is not a superuser.
        :raises BadRequestError: If the registry has no such extension or version, or it is incompatible.
        """
        body: SmarterJsonObjectType = {"slug": slug}
        if version:
            body["version"] = version
        return self._http.request("POST", f"{self.path}install/", json=body, cast_to=ExtensionActionResult)

    def upload(self, archive: ExtensionArchive) -> ExtensionActionResult:
        """
        Install, or update, an extension from its .zip archive.

        Superusers only. It is installed disabled. The platform's trust badge of an uploaded
        extension is ``unverified``.

        :param archive: The archive's path, or a binary file object. At most 10 MiB.
        :returns: A message, and the installed extension.
        :raises PermissionDeniedError: If the user is not a superuser.
        :raises BadRequestError: If the archive is not a valid extension.
        """
        if isinstance(archive, (str, Path)):
            with open(Path(archive), "rb") as handle:
                return self._upload(Path(archive).name, handle)
        return self._upload(Path(str(getattr(archive, "name", "") or "extension.zip")).name, archive)

    def _upload(self, filename: str, handle: IO[bytes]) -> ExtensionActionResult:
        return self._http.request(
            "POST",
            f"{self.path}upload/",
            files={"archive": (filename, handle, "application/zip")},
            cast_to=ExtensionActionResult,
        )

    def _action(self, slug: str, action: str, body: SmarterJsonObjectType | None = None) -> ExtensionActionResult:
        return self._http.request(
            "POST", f"{self.path}{resource_id(slug)}/{action}/", json=body, cast_to=ExtensionActionResult
        )

    def enable(self, slug: str) -> ExtensionActionResult:
        """
        Enable an extension, after the platform checks that it is compatible, loads, and has its required settings.

        Superusers only. Its tools are then offered to the LLMClients that use it.

        :param slug: The extension's slug.
        :returns: A message, and the extension.
        :raises PermissionDeniedError: If the user is not a superuser.
        :raises BadRequestError: If it cannot be enabled, e.g. a required setting is missing.
        """
        return self._action(slug, "enable")

    def disable(self, slug: str) -> ExtensionActionResult:
        """
        Disable an extension.

        Superusers only.

        :param slug: The extension's slug.
        :returns: A message, and the extension.
        :raises PermissionDeniedError: If the user is not a superuser.
        """
        return self._action(slug, "disable")

    def update(self, slug: str) -> ExtensionActionResult:
        """
        Install the registry's newest compatible version of an extension.

        Superusers only.

        :param slug: The extension's slug.
        :returns: A message, and the extension.
        :raises PermissionDeniedError: If the user is not a superuser.
        """
        return self._action(slug, "update")

    def rollback(self, slug: str, version_id: int) -> ExtensionActionResult:
        """
        Make one of an extension's earlier installed versions the one that runs.

        Superusers only.

        :param slug: The extension's slug.
        :param version_id: The version's id, from the extension's ``versions``.
        :returns: A message, and the extension.
        :raises PermissionDeniedError: If the user is not a superuser.
        """
        return self._action(slug, "rollback", {"versionId": version_id})

    def configure(
        self,
        slug: str,
        *,
        values: Mapping[str, ExtensionSettingValue] | None = None,
        secrets: Mapping[str, ExtensionSecretValue] | None = None,
    ) -> ExtensionActionResult:
        """
        Change some of an extension's settings.

        Superusers only. Settings that are left out don't change.

        .. code-block:: python

            client.extensions.configure(
                "weather",
                values={"weather_api_url": None},             # None resets it to its default
                secrets={"google_maps_api_key": 6},           # one of the platform admin's Secrets, by id
            )

        :param slug: The extension's slug.
        :param values: Non-secret settings' values, by name. None resets a setting to its default.
        :param secrets: Secret settings' values, by name: a string is saved encrypted in a new
            Secret of the platform admin, an integer is the id of one of the platform admin's
            Secrets, and None clears the setting.
        :returns: A message, and the extension.
        :raises PermissionDeniedError: If the user is not a superuser.
        :raises BadRequestError: If a setting does not exist, or a value is invalid.
        """
        secret_inputs: dict[str, SmarterJsonType] = {}
        for name, secret in (secrets or {}).items():
            if isinstance(secret, str):
                secret_inputs[name] = {"value": secret}
            elif isinstance(secret, int) and not isinstance(secret, bool):
                secret_inputs[name] = {"secretId": secret}
            else:
                secret_inputs[name] = {}
        body: SmarterJsonObjectType = {"values": dict(values or {}), "secrets": secret_inputs}
        return self._action(slug, "configure", body)

    def set_availability(
        self, slug: str, all_accounts: bool, account_ids: Iterable[int] | None = None
    ) -> ExtensionActionResult:
        """
        Make an extension available to every account, or to the given accounts only.

        Superusers only.

        :param slug: The extension's slug.
        :param all_accounts: True for every account.
        :param account_ids: The ids of the accounts that may use it, when ``all_accounts`` is False.
        :returns: A message, and the extension.
        :raises PermissionDeniedError: If the user is not a superuser.
        :raises BadRequestError: If some of the accounts do not exist.
        """
        body: SmarterJsonObjectType = {"allAccounts": all_accounts, "accountIds": list(account_ids or [])}
        return self._action(slug, "availability", body)

    def uninstall(self, slug: str) -> ExtensionActionResult:
        """
        Uninstall an extension, and delete its versions and settings.

        Superusers only.

        :param slug: The extension's slug.
        :returns: A message. Its ``extension`` is None.
        :raises PermissionDeniedError: If the user is not a superuser.
        """
        return self._action(slug, "uninstall")


__all__ = ["ExtensionArchive", "ExtensionSecretValue", "Extensions"]
