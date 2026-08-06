"""
Base MCP tool for Django Boost.

Provides common utilities for all tools.
"""

from typing import Any

from mcp.types import Tool as McpTool


class BoostTool:
    """Base class for Django Boost MCP tools."""

    name: str = ""
    description: str = ""
    is_read_only: bool = True

    def to_mcp_tool(self) -> McpTool:
        """Convert to an MCP Tool descriptor."""
        return McpTool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema(),
        )

    def input_schema(self) -> dict[str, Any]:
        """Return the JSON Schema for the tool's input parameters."""
        return {"type": "object", "properties": {}}

    async def call(self, arguments: dict[str, Any]) -> list[Any]:
        """Execute the tool. Subclasses override this."""
        raise NotImplementedError

    def _ok(self, text: str) -> list[dict]:
        """Return a successful text response."""
        return [{"type": "text", "text": text}]

    def _json(self, data: Any) -> list[dict]:
        """Return a successful JSON response."""
        import json

        return [{"type": "text", "text": json.dumps(data, indent=2, default=str)}]

    def _error(self, message: str) -> list[dict]:
        """Return an error response."""
        return [{"type": "text", "text": f"Error: {message}", "isError": True}]
