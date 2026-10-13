"""
MCPClients: the platform's connections to Model Context Protocol servers.

.. code-block:: python

    tools = client.mcp_clients.tools(1)
    result = client.mcp_clients.call_tool(1, "aws___search_documentation", {"search_phrase": "S3"})
    print(result.content)
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional

from smarter.core.typing import SmarterIdType, SmarterJsonType
from smarter.models.mcpclient import (
    MCPClient,
    MCPClientStatus,
    MCPClientTools,
    MCPToolResult,
)

from .base import SmarterKindResource, resource_id


class MCPClients(SmarterKindResource[MCPClient]):
    """MCPClients: ``/api/v1/mcpclients/``, and the manifest api's ``MCPClient`` kind."""

    kind = "MCPClient"
    path = "mcpclients/"
    model = MCPClient

    def tools(self, id: SmarterIdType, *, refresh: bool = False) -> MCPClientTools:  # pylint: disable=redefined-builtin
        """
        The tools that an MCPClient allows the LLM to call, from the server's cached catalog.

        :param id: The MCPClient's id or hashed id.
        :param refresh: True to read the catalog from the server now.
        :returns: The connection's state, the server's instructions, and the tools.
        """
        return self._http.request(
            "GET", f"{self.path}{resource_id(id)}/tools/", params={"refresh": refresh or None}, cast_to=MCPClientTools
        )

    def refresh(self, id: SmarterIdType) -> MCPClientStatus:  # pylint: disable=redefined-builtin
        """
        Reconnect to an MCPClient's server, and reload its catalog.

        Only the owner may refresh.

        :param id: The MCPClient's id or hashed id.
        :returns: The connection's state.
        """
        return self._http.request("POST", f"{self.path}{resource_id(id)}/refresh/", cast_to=MCPClientStatus)

    def call_tool(
        self,
        id: SmarterIdType,  # pylint: disable=redefined-builtin
        tool: str,
        arguments: Mapping[str, SmarterJsonType] | None = None,
    ) -> MCPToolResult:
        """
        Call one of an MCPClient's tools.

        Only the owner may call tools.

        :param id: The MCPClient's id or hashed id.
        :param tool: The tool's name.
        :param arguments: The tool's arguments, as its input schema describes them.
        :returns: The tool's result. Check ``is_error``: a tool reports its own failures in its result.
        """
        return self._http.request(
            "POST",
            f"{self.path}{resource_id(id)}/tools/{resource_id(tool)}/",
            json=dict(arguments or {}),
            cast_to=MCPToolResult,
        )


__all__ = ["MCPClients"]
