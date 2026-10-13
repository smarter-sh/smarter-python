"""
Proxies: authenticated passthrough access to LLM providers' own apis.

The platform holds the provider's api key, and callers use their Smarter api key instead. The
easiest way to call a proxy is with the provider's own SDK:

.. code-block:: python

    from openai import OpenAI
    from smarter import Smarter

    smarter = Smarter()
    openai = OpenAI(base_url=smarter.proxies.base_url("openai"), api_key=smarter.api_key)
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional

from smarter.core.http import QueryParamValue
from smarter.core.typing import SmarterJsonType
from smarter.models.misc import Proxies as ProxiesModel
from smarter.models.misc import Proxy

from .base import SmarterAPIResource, resource_id


class Proxies(SmarterAPIResource):
    """
    Proxies: ``/api/v1/proxy/``.

    The platform serves these endpoints only when ``SMARTER_ENABLE_PROXY`` is true.
    """

    path = "proxy/"

    def list(self) -> list[Proxy]:
        """
        The proxies that the user may call.

        :returns: The proxies.
        """
        return self._http.request("GET", self.path, cast_to=ProxiesModel).proxies

    def base_url(self, name: str) -> str:
        """
        A proxy's base url, for the provider's own SDK.

        :param name: The proxy's name, e.g. ``openai``.
        :returns: e.g. ``https://platform.smarter.sh/api/v1/proxy/openai/``.
        """
        return self._http.url(f"{self.path}{resource_id(name)}/")

    def request(
        self,
        name: str,
        path: str,
        *,
        method: str = "POST",
        json: SmarterJsonType = None,
        params: Mapping[str, QueryParamValue] | None = None,
    ) -> SmarterJsonType:
        """
        Send a request to a provider's api, through its proxy.

        :param name: The proxy's name, e.g. ``openai``.
        :param path: The provider api's path, e.g. ``v1/chat/completions``. It must be one of the proxy's ``allowed_paths``.
        :param method: The http method.
        :param json: The JSON body, as the provider's api expects it.
        :param params: Query parameters.
        :returns: The provider's JSON response.
        """
        return self._http.request(
            method.upper(),
            f"{self.path}{resource_id(name)}/{path.lstrip('/')}",
            json=json,
            params=params,
            cast_to=SmarterJsonType,
        )


__all__ = ["Proxies"]
