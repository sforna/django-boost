"""
Tests for MCP tool base class and individual tools.
"""

from django_boost.mcp.tools.base import BoostTool


class FakeReadTool(BoostTool):
    name = "fake-read"
    description = "A fake read-only tool"
    is_read_only = True

    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "arg1": {"type": "string", "description": "First arg"},
            },
            "required": ["arg1"],
        }

    async def call(self, arguments: dict):
        return self._ok(f"Got: {arguments.get('arg1', '')}")


class TestBoostTool:
    """Tests for the BoostTool base class."""

    def test_to_mcp_tool(self):
        """Should produce a valid MCP tool descriptor."""
        tool = FakeReadTool()
        mcp = tool.to_mcp_tool()
        assert mcp.name == "fake-read"
        assert mcp.description == "A fake read-only tool"
        assert "arg1" in mcp.input_schema.get("properties", {})

    def test_ok_response(self):
        """_ok should return a text response list."""
        tool = FakeReadTool()
        response = tool._ok("hello")
        assert response == [{"type": "text", "text": "hello"}]

    def test_json_response(self):
        """_json should serialize to indented JSON."""
        tool = FakeReadTool()
        response = tool._json({"key": "value"})
        assert response[0]["type"] == "text"
        assert '"key": "value"' in response[0]["text"]

    def test_error_response(self):
        """_error should include isError flag."""
        tool = FakeReadTool()
        response = tool._error("Something went wrong")
        assert response[0]["type"] == "text"
        assert response[0]["isError"] is True
        assert "Error:" in response[0]["text"]

    def test_call_dispatches_to_subclass(self):
        """Should execute subclass call() method."""
        import asyncio

        tool = FakeReadTool()
        result = asyncio.run(tool.call({"arg1": "world"}))
        assert result[0]["text"] == "Got: world"
