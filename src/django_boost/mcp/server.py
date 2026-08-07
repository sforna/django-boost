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
import django_boost.mcp.tools.application_info as _app_info  # noqa: F401,E402
import django_boost.mcp.tools.browser_logs as _browser_logs  # noqa: F401,E402
import django_boost.mcp.tools.database_connections as _db_conns  # noqa: F401,E402
import django_boost.mcp.tools.database_query as _db_query  # noqa: F401,E402
import django_boost.mcp.tools.database_schema.tool as _db_schema  # noqa: F401,E402
import django_boost.mcp.tools.get_absolute_url as _abs_url  # noqa: F401,E402
import django_boost.mcp.tools.last_error as _last_error  # noqa: F401,E402
import django_boost.mcp.tools.read_log_entries as _log_entries  # noqa: F401,E402
import django_boost.mcp.tools.record_rule as _record_rule  # noqa: F401,E402
import django_boost.mcp.tools.search_docs as _search_docs  # noqa: F401,E402
import django_boost.mcp.tools.tinker as _tinker  # noqa: F401,E402
