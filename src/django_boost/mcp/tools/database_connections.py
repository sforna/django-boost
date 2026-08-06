"""
DatabaseConnections tool — lists configured database connection names.

Equivalent to Laravel Boost's DatabaseConnections tool.
"""

from .base import BoostTool


class DatabaseConnections(BoostTool):
    """List the configured database connection names for this application."""

    name = "database-connections"
    description = "List the configured database connection names for this application."
    is_read_only = True

    async def call(self, arguments: dict) -> list[dict]:
        from django.conf import settings

        connections = list(settings.DATABASES.keys())
        return self._json({
            "default_connection": getattr(
                settings, "DATABASE_DEFAULT", connections[0] if connections else None
            ),
            "connections": connections,
        })
