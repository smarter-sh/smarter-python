"""Test smarter.resources.mcpclients."""

from .base import SmarterTestBase


class TestMCPClients(SmarterTestBase):
    """Test MCPClients."""

    def test_list(self):
        """MCPClients are listed with their connection state."""
        self.route("GET", "mcpclients/", fixture="mcpclients")
        mcpclient = self.client.mcp_clients.list()[0]
        self.assertEqual(mcpclient.status, "connected")
        self.assertTrue(mcpclient.allowed_tools)

    def test_tools(self):
        """Tools() returns the allowed tools, and asks for a refresh only when told to."""
        self.route("GET", "mcpclients/1/tools/", fixture="mcp_tools")
        tools = self.client.mcp_clients.tools(1)
        self.assertEqual(tools.tools[0].name, "aws___read_documentation")
        self.assertNotIn("refresh", self.last_request.url.params)
        self.client.mcp_clients.tools(1, refresh=True)
        self.assertEqual(self.last_request.url.params["refresh"], "true")

    def test_refresh(self):
        """Refresh() returns the connection's state."""
        self.route("POST", "mcpclients/1/refresh/", json_body={"name": "aws_knowledge", "status": "connected"})
        self.assertEqual(self.client.mcp_clients.refresh(1).status, "connected")

    def test_call_tool(self):
        """``call_tool()`` sends the arguments as the JSON body, and returns the tool's result."""
        result = {"name": "aws_knowledge", "tool": "aws___list_regions", "isError": False, "content": "us-east-1"}
        self.route("POST", "mcpclients/1/tools/aws___list_regions/", json_body=result)
        response = self.client.mcp_clients.call_tool(1, "aws___list_regions", {"limit": 1})
        self.assertFalse(response.is_error)
        self.assertEqual(response.content, "us-east-1")
        self.assertEqual(self.request_json(), {"limit": 1})
        self.client.mcp_clients.call_tool(1, "aws___list_regions")
        self.assertEqual(self.request_json(), {})
