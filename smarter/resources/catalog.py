"""Secrets, plugins, orchestrators and vectorsearches: the kinds whose REST api only lists and reads them."""

from __future__ import annotations

from smarter.core.exceptions import SmarterValueError
from smarter.core.typing import SmarterIdType
from smarter.models.journal import SmarterJournalMessage
from smarter.models.manifest import Manifest
from smarter.models.misc import Orchestrator, Secret, Vectorsearch
from smarter.models.plugin import Plugin

from .base import ManifestInput, SmarterKindResource, resource_id, to_manifest

PLUGIN_KINDS = ("Plugin", "ApiPlugin", "SkillPlugin", "SqlPlugin", "WebsearchPlugin", "ImageSearchPlugin")
"""The manifest kinds of plugins."""


class Secrets(SmarterKindResource[Secret]):
    """
    Secrets: ``/api/v1/secrets/``, and the manifest api's ``Secret`` kind.

    The api never returns a secret's value. Create and rotate secrets with :meth:`apply`.
    """

    kind = "Secret"
    path = "secrets/"
    model = Secret


class Plugins(SmarterKindResource[Plugin]):
    """
    Plugins: ``/api/v1/plugins/``, and the manifest api's plugin kinds.

    A plugin's manifest kind is its class, e.g. ``ApiPlugin`` or ``SqlPlugin``. :meth:`apply`
    accepts any of them, and :meth:`describe` and :meth:`delete` look the kind up by name.
    """

    kind = "Plugin"
    path = "plugins/"
    model = Plugin

    def apply(self, manifest: ManifestInput) -> SmarterJournalMessage:
        """
        Create or update a plugin from its manifest, of any plugin kind.

        :param manifest: The manifest.
        :returns: The platform's response.
        :raises SmarterValueError: If the manifest is not a plugin's.
        """
        parsed = to_manifest(manifest)
        if parsed.kind not in PLUGIN_KINDS:
            raise SmarterValueError(f"Expected a plugin manifest ({', '.join(PLUGIN_KINDS)}), not {parsed.kind}.")
        return self._client.manifests.apply(parsed)

    def kind_of(self, name: str) -> str:
        """
        A plugin's manifest kind.

        :param name: The plugin's name.
        :returns: e.g. ``SqlPlugin``.
        """
        return self.find(name).kind or self.kind

    def describe(self, name: str) -> Manifest:
        """
        A plugin's manifest, with its read-only ``status``.

        :param name: The plugin's name.
        :returns: The manifest.
        """
        return self._client.manifests.describe(self.kind_of(name), name)

    def delete(self, name: str) -> SmarterJournalMessage:
        """
        Permanently delete a plugin.

        :param name: The plugin's name.
        :returns: The platform's response.
        """
        return self._client.manifests.delete(self.kind_of(name), name)

    def retrieve(self, id: SmarterIdType) -> Manifest:  # type: ignore[override]  # pylint: disable=redefined-builtin
        """
        One plugin's manifest, by the plugin's id.

        The platform serves this only when its ``ALLOW_API_GET`` waffle switch is on. Otherwise it
        answers 405: use :meth:`find` or :meth:`describe` instead.

        :param id: The plugin's id.
        :returns: The plugin's manifest, whose ``kind`` is the plugin's, e.g. ``SqlPlugin``.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/", cast_to=Manifest)


class Orchestrators(SmarterKindResource[Orchestrator]):
    """Orchestrators: ``/api/v1/orchestrators/``, and the manifest api's ``Orchestrator`` kind."""

    kind = "Orchestrator"
    path = "orchestrators/"
    model = Orchestrator


class Vectorsearches(SmarterKindResource[Vectorsearch]):
    """Vectorsearches: ``/api/v1/vectorsearches/``, and the manifest api's ``Vectorsearch`` kind."""

    kind = "Vectorsearch"
    path = "vectorsearches/"
    model = Vectorsearch


__all__ = ["Orchestrators", "PLUGIN_KINDS", "Plugins", "Secrets", "Vectorsearches"]
