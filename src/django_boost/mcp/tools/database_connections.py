"""
DatabaseConnections tool — lists configured database connection names.
"""

from django_boost.mcp.server import mcp


@mcp.tool(
    name="database-connections",
    description="List the configured database connection names for this application.",
    annotations={"readOnlyHint": True},
)
def database_connections() -> dict:
    """Return the list of configured database connections."""
    from django.conf import settings

    connections = list(settings.DATABASES.keys())
    return {
        "default_connection": getattr(
            settings, "DATABASE_DEFAULT", connections[0] if connections else None
        ),
        "connections": connections,
    }
