"""LLM providers and their models: ``/api/v1/providers/``."""

from __future__ import annotations

from smarter.models.misc import Provider, ProviderModel

from .base import SmarterAPIResource, resource_id


class Providers(SmarterAPIResource):
    """The LLM providers that the platform is configured for, e.g. openai or anthropic."""

    path = "providers/"

    def list(self) -> list[Provider]:
        """
        The providers.

        :returns: The providers.
        """
        return self._http.request("GET", self.path, cast_to=list[Provider])

    def retrieve(self, name: str) -> Provider:
        """
        A provider, by name.

        :param name: The provider's name, e.g. ``openai``.
        :returns: The provider.
        """
        return self._http.request("GET", f"{self.path}{resource_id(name)}/", cast_to=Provider)

    def models(self, name: str) -> list[ProviderModel]:
        """
        A provider's models.

        :param name: The provider's name.
        :returns: The models.
        """
        return self._http.request("GET", f"{self.path}{resource_id(name)}/models/", cast_to=list[ProviderModel])


__all__ = ["Providers"]
