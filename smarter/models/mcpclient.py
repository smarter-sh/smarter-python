"""Models of MCPClients: connections to Model Context Protocol servers, whose tools an LLMClient's LLM can call."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from smarter.core.typing import SmarterJsonObjectType

from .base import SmarterCamelModel, SmarterResource


class MCPClient(SmarterResource):
    """An MCPClient: an MCP server, how to reach it, and which of its tools the LLM may call."""

    transport: Optional[str] = Field(None, description="http, sse or stdio.")
    endpoint_url: Optional[str] = None
    command: Optional[str] = None
    timeout: Optional[int] = None
    auth_type: Optional[str] = None
    allowed_tools: list[str] = []
    allowed_resources: list[str] = []
    include_instructions: Optional[bool] = None
    cache_ttl: Optional[int] = None
    is_active: Optional[bool] = None
    status: Optional[str] = Field(None, description="e.g. connected or error.")
    priority: Optional[int] = None
    protocol_version: Optional[str] = None
    server_name: Optional[str] = None
    server_version: Optional[str] = None
    tools: list[str] = Field(default_factory=list, description="The names of every tool that the server offers.")
    last_connected_at: Optional[datetime] = None
    last_error: Optional[str] = None


class MCPClientStatus(SmarterCamelModel):
    """The connection state of an MCPClient."""

    name: str
    status: Optional[str] = None
    protocol_version: Optional[str] = None
    server_name: Optional[str] = None
    server_version: Optional[str] = None
    last_connected: Optional[datetime] = None
    last_error: Optional[str] = None
    error: Optional[str] = Field(None, description="The error of a failed refresh.")


class MCPTool(SmarterCamelModel):
    """A tool of an MCP server, which the MCPClient allows the LLM to call."""

    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[SmarterJsonObjectType] = Field(None, description="The tool's arguments, as a JSON Schema.")
    read_only: Optional[bool] = None
    destructive: Optional[bool] = None


class MCPClientTools(MCPClientStatus):
    """An MCPClient's allowed tools, and the server's instructions."""

    instructions: Optional[str] = None
    tools: list[MCPTool] = []


class MCPToolResult(SmarterCamelModel):
    """The result of a tool call."""

    name: str = Field(..., description="The MCPClient's name.")
    tool: str
    is_error: bool = False
    content: Optional[str] = Field(None, description="The tool's result, as text.")


__all__ = ["MCPClient", "MCPClientStatus", "MCPClientTools", "MCPTool", "MCPToolResult"]
