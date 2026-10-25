"""
The Smarter client.

.. code-block:: python

    from smarter import Smarter

    client = Smarter()                      # SMARTER_API_KEY, or ~/.smarter/config.yaml
    print(client.whoami().user.username)

    response = client.llm_clients.prompt(5, "What is 17 times 23?")
    print(response.text)
"""

from collections.abc import Mapping
from functools import cached_property
from types import TracebackType
from typing import Any

import httpx

from smarter.core.conf import (
    SmarterEnvironment,
    SmarterSettings,
    resolve_client_config,
)
from smarter.core.http import SmarterHttpClient
from smarter.core.log import mask_secret, setup_logging
from smarter.models.journal import SmarterJournaledResponse
from smarter.models.manifest import KindInfo
from smarter.models.platform import PlatformStatus, PlatformVersion, WhoAmI
from smarter.resources import (
    Accounts,
    Guardrails,
    Journal,
    LLMClients,
    LLMHosts,
    Manifests,
    MCPClients,
    Orchestrators,
    Plugins,
    PromptHistory,
    Providers,
    Proxies,
    Secrets,
    Vectorsearches,
    Vectorstores,
)


class Smarter:
    """
    A client of a Smarter platform's api.

    Every argument is optional. See :mod:`smarter.core.conf` for where each is looked up.

    :param api_key: A Smarter api key.
    :param base_url: The platform's url, e.g. ``https://platform.example.com`` or ``http://localhost:9357``.
    :param environment: The environment of the smarter cli's configuration file to use: ``local``,
        ``alpha``, ``beta``, ``next`` or ``prod``.
    :param timeout: The request timeout, in seconds.
    :param max_retries: How many times to retry a request that failed for a transient reason, e.g.
        a timeout, a 429 or a 502. 0 disables retries.
    :param default_headers: Headers to add to every request.
    :param http_client: An ``httpx.Client`` to send the requests, e.g. one with a proxy. The client
        does not close a client that it was given.
    :raises SmarterConfigurationError: If no api key is found.

    The client's attributes group the api's operations:

    - :attr:`manifests`: apply, validate, get, describe, delete, deploy, undeploy and logs, for any kind
    - :attr:`llm_clients`: LLMClients, and prompting and chatting with them
    - :attr:`guardrails`, :attr:`mcp_clients`, :attr:`vectorstores`, :attr:`llm_hosts`,
      :attr:`secrets`, :attr:`plugins`, :attr:`orchestrators`, :attr:`vectorsearches`
    - :attr:`accounts` (and ``accounts.users`` and ``accounts.contacts``)
    - :attr:`history`, :attr:`journal`, :attr:`providers`, :attr:`proxies`
    - :meth:`whoami`, :meth:`version`, :meth:`status` and :meth:`kinds`

    Use it as a context manager, or call :meth:`close`, to close its connections.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        environment: SmarterEnvironment | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        default_headers: Mapping[str, str] | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        settings = SmarterSettings()
        setup_logging(settings.log)
        self.config = resolve_client_config(
            api_key=api_key,
            base_url=base_url,
            environment=environment,
            timeout=timeout,
            max_retries=max_retries,
            settings=settings,
        )
        self.http = SmarterHttpClient(self.config, default_headers=default_headers, http_client=http_client)
        """The http transport, for endpoints that the SDK does not wrap."""

    @property
    def api_key(self) -> str:
        """The api key, e.g. to use a proxy with a provider's own SDK."""
        return self.config.api_key.get_secret_value()

    @property
    def base_url(self) -> str:
        """The api's base url, e.g. ``https://platform.smarter.sh/api/v1/``."""
        return self.config.base_url

    @cached_property
    def manifests(self) -> Manifests:
        """The manifest api, for any resource kind."""
        return Manifests(self)

    @cached_property
    def llm_clients(self) -> LLMClients:
        """LLMClients."""
        return LLMClients(self)

    @cached_property
    def guardrails(self) -> Guardrails:
        """Guardrails."""
        return Guardrails(self)

    @cached_property
    def mcp_clients(self) -> MCPClients:
        """MCPClients."""
        return MCPClients(self)

    @cached_property
    def vectorstores(self) -> Vectorstores:
        """Vectorstores."""
        return Vectorstores(self)

    @cached_property
    def llm_hosts(self) -> LLMHosts:
        """LLMHosts."""
        return LLMHosts(self)

    @cached_property
    def secrets(self) -> Secrets:
        """Secrets."""
        return Secrets(self)

    @cached_property
    def plugins(self) -> Plugins:
        """Plugins."""
        return Plugins(self)

    @cached_property
    def orchestrators(self) -> Orchestrators:
        """Orchestrators."""
        return Orchestrators(self)

    @cached_property
    def vectorsearches(self) -> Vectorsearches:
        """Vectorsearches."""
        return Vectorsearches(self)

    @cached_property
    def accounts(self) -> Accounts:
        """Accounts, and their users and contacts."""
        return Accounts(self)

    @cached_property
    def history(self) -> PromptHistory:
        """The history of chat sessions, tool calls and plugin uses."""
        return PromptHistory(self)

    @cached_property
    def journal(self) -> Journal:
        """The Smarter Journal.

        Superusers only.
        """
        return Journal(self)

    @cached_property
    def providers(self) -> Providers:
        """LLM providers and their models."""
        return Providers(self)

    @cached_property
    def proxies(self) -> Proxies:
        """Proxies to LLM providers' own apis."""
        return Proxies(self)

    def whoami(self) -> WhoAmI:
        """
        The owner of the api key: the user, their account, and the platform's environment.

        :returns: The owner.
        """
        return self._cli_data("whoami/", WhoAmI)

    def version(self) -> PlatformVersion:
        """
        The platform's version, and the versions of its main Python packages.

        :returns: The versions.
        """
        return self._cli_data("version/", PlatformVersion)

    def status(self) -> PlatformStatus:
        """
        The state of the platform's infrastructure and compute.

        :returns: The status.
        """
        return self._cli_data("status/", PlatformStatus)

    def kinds(self) -> list[KindInfo]:
        """
        The resource kinds that the platform supports, and which of them can be deployed.

        :returns: The kinds.
        """
        return self._cli_data("resources/", list[KindInfo])

    def _cli_data(self, path: str, cast_to: Any) -> Any:
        """
        The ``data`` of a journaled response of the cli api.

        :param path: The cli endpoint's path, e.g. ``whoami/``.
        :param cast_to: The type of the ``data``: any type form that Pydantic validates, e.g. ``list[KindInfo]``.
        :returns: The validated ``data``.
        """
        response = self.http.request("POST", f"cli/{path}", cast_to=SmarterJournaledResponse[cast_to])
        return response.data

    def close(self) -> None:
        """Close the client's connections."""
        self.http.close()

    def __enter__(self) -> "Smarter":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"Smarter(base_url={self.base_url!r}, api_key={mask_secret(self.api_key)!r})"


__all__ = ["Smarter"]
