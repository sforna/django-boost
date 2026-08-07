"""
MCP Server for Django Boost.

Powered by FastMCP — tools are registered via @mcp.tool decorators
at module-import time. Simply importing each tool module below triggers
registration on the shared ``mcp`` instance.
"""

from fastmcp import FastMCP

from django_boost import __version__

# ---------------------------------------------------------------------------
# The single FastMCP instance — tool modules import this to decorate their
# functions with @mcp.tool().
# ---------------------------------------------------------------------------
mcp = FastMCP(
    name="django-boost",
    version=__version__,
    instructions=(
        "Django Boost — AI-assisted development accelerator. "
        "Exposes Django ecosystem tools: database schema, error logs, "
        "documentation search, and more."
    ),
)


def create_server() -> FastMCP:
    """Return the pre-configured FastMCP server instance.

    Used by pyproject.toml entry_points and external callers.
    """
    return mcp


async def run_server() -> None:
    """Run the MCP server with stdio transport (legacy wrapper)."""
    mcp.run()


# ---------------------------------------------------------------------------
# Import tool modules so @mcp.tool decorators fire and self-register.
# Each module imports ``mcp`` from here and applies @mcp.tool on a function.
# The noqa comments silence "unused import" lints.
# ---------------------------------------------------------------------------
import django_boost.mcp.tools.application_info as _  # noqa: E402,F811
import django_boost.mcp.tools.browser_logs as _  # noqa: E402,F811
import django_boost.mcp.tools.database_connections as _  # noqa: E402,F811
import django_boost.mcp.tools.database_query as _  # noqa: E402,F811
import django_boost.mcp.tools.database_schema.tool as _  # noqa: E402,F811
import django_boost.mcp.tools.get_absolute_url as _  # noqa: E402,F811
import django_boost.mcp.tools.last_error as _  # noqa: E402,F811
import django_boost.mcp.tools.read_log_entries as _  # noqa: E402,F811
import django_boost.mcp.tools.record_rule as _  # noqa: E402,F811
import django_boost.mcp.tools.search_docs as _  # noqa: E402,F811
import django_boost.mcp.tools.tinker as _  # noqa: E402,F811
