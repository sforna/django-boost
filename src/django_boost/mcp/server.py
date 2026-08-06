"""
MCP Server for Django Boost.

Provides the core Model Context Protocol server that exposes Django-specific
tools to AI coding agents.
"""

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server

from django_boost import __version__

from .tools.application_info import ApplicationInfo
from .tools.browser_logs import BrowserLogs
from .tools.database_connections import DatabaseConnections
from .tools.database_query import DatabaseQuery
from .tools.database_schema import DatabaseSchema
from .tools.get_absolute_url import GetAbsoluteUrl
from .tools.last_error import LastError
from .tools.read_log_entries import ReadLogEntries
from .tools.record_rule import RecordRule
from .tools.search_docs import SearchDocs
from .tools.tinker import Tinker


class DjangoBoostServer(Server):
    """Django Boost MCP Server.

    Exposes Django ecosystem tools: database schema access, error logs,
    semantic documentation search, and more.
    """

    def __init__(self):
        super().__init__(
            name="django-boost",
            version=__version__,
        )
        self._tools = []

    def register_tools(self) -> None:
        """Register all available MCP tools."""
        tools = [
            ApplicationInfo(),
            BrowserLogs(),
            DatabaseConnections(),
            DatabaseQuery(),
            DatabaseSchema(),
            GetAbsoluteUrl(),
            LastError(),
            ReadLogEntries(),
            SearchDocs(),
        ]
        # RecordRule: opt-in via rules.enabled
        rule = RecordRule()
        if rule.should_register():
            tools.append(rule)
        # Tinker: opt-in via settings
        tinker = Tinker()
        if tinker.should_register():
            tools.append(tinker)
        self._tools = tools

    def list_tools(self):
        """Return all registered tools."""
        return [t.to_mcp_tool() for t in self._tools]

    async def call_tool(self, name: str, arguments: dict):
        """Call a tool by name."""
        for tool in self._tools:
            if tool.name == name:
                return await tool.call(arguments)
        raise ValueError(f"Tool not found: {name}")


def create_server() -> DjangoBoostServer:
    """Factory to create a configured Django Boost MCP server."""
    server = DjangoBoostServer()
    server.register_tools()
    return server


async def run_server() -> None:
    """Run the MCP server with stdio transport."""
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
