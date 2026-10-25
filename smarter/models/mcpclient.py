"""Models of MCPClients: connections to Model Context Protocol servers, whose tools an LLMClient's LLM can call."""

from datetime import datetime

from pydantic import Field

from smarter.core.typing import SmarterJsonObjectType

from .base import SmarterCamelModel, SmarterResource


class MCPClient(SmarterResource):
    """An MCPClient: an MCP server, how to reach it, and which of its tools the LLM may call."""

    transport: str | None = Field(None, description="http, sse or stdio.")
    endpoint_url: str | None = None
    command: str | None = None
    timeout: int | None = None
    auth_type: str | None = None
    allowed_tools: list[str] = []
    allowed_resources: list[str] = []
    include_instructions: bool | None = None
    cache_ttl: int | None = None
    is_active: bool | None = None
    status: str | None = Field(None, description="e.g. connected or error.")
    priority: int | None = None
    protocol_version: str | None = None
    server_name: str | None = None
    server_version: str | None = None
    tools: list[str] = Field(default_factory=list, description="The names of every tool that the server offers.")
    last_connected_at: datetime | None = None
    last_error: str | None = None


class MCPClientStatus(SmarterCamelModel):
    """The connection state of an MCPClient."""

    name: str
    status: str | None = None
    protocol_version: str | None = None
    server_name: str | None = None
    server_version: str | None = None
    last_connected: datetime | None = None
    last_error: str | None = None
    error: str | None = Field(None, description="The error of a failed refresh.")


class MCPTool(SmarterCamelModel):
    """A tool of an MCP server, which the MCPClient allows the LLM to call."""

    name: str
    title: str | None = None
    description: str | None = None
    input_schema: SmarterJsonObjectType | None = Field(None, description="The tool's arguments, as a JSON Schema.")
    read_only: bool | None = None
    destructive: bool | None = None


class MCPClientTools(MCPClientStatus):
    """An MCPClient's allowed tools, and the server's instructions."""

    instructions: str | None = None
    tools: list[MCPTool] = []


class MCPToolResult(SmarterCamelModel):
    """The result of a tool call."""

    name: str = Field(..., description="The MCPClient's name.")
    tool: str
    is_error: bool = False
    content: str | None = Field(None, description="The tool's result, as text.")


__all__ = ["MCPClient", "MCPClientStatus", "MCPClientTools", "MCPTool", "MCPToolResult"]
