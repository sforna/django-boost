"""
DatabaseQuery tool — execute read-only SQL queries.

Equivalent to Laravel Boost's DatabaseQuery tool.
"""

from typing import Any

from django.db import connection, connections

from .base import BoostTool
from .sql_validator import is_read_only_query


class DatabaseQuery(BoostTool):
    """Execute a read-only SQL query against the configured database.

    Only SELECT, SHOW, EXPLAIN, DESCRIBE, DESC, WITH...SELECT,
    VALUES, and TABLE queries are allowed.
    """

    name = "database-query"
    description = "Execute a read-only SQL query against the configured database."
    is_read_only = True

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The SQL query to execute. Only read-only queries "
                        "are allowed (SELECT, SHOW, EXPLAIN, DESCRIBE)."
                    ),
                },
                "database": {
                    "type": "string",
                    "description": (
                        "Optional database connection name. "
                        "Defaults to the application's default connection."
                    ),
                },
            },
            "required": ["query"],
        }

    async def call(self, arguments: dict) -> list[dict]:
        query = arguments.get("query", "").strip()

        if not query:
            return self._error("Please pass a valid query.")

        if not is_read_only_query(query):
            return self._error(
                "Only read-only queries are allowed "
                "(SELECT, SHOW, EXPLAIN, DESCRIBE, DESC, WITH … SELECT)."
            )

        db_name = arguments.get("database")

        try:
            conn = connections[db_name] if db_name else connection

            with conn.cursor() as cursor:
                cursor.execute(query)

                # Get column names
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = []
                    for row in cursor.fetchall():
                        rows.append(dict(zip(columns, row)))
                    return self._json(rows)
                else:
                    return self._ok("Query executed (no rows returned).")

        except Exception as e:
            return self._error(f"Query failed: {e}")
