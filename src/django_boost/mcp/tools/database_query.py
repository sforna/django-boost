"""
DatabaseQuery tool — execute read-only SQL queries.
"""

from django.db import connection, connections

from django_boost.mcp.server import mcp
from .sql_validator import is_read_only_query


@mcp.tool(
    name="database-query",
    description="Execute a read-only SQL query against the configured database.",
    annotations={"readOnlyHint": True},
)
def database_query(
    query: str,
    database: str | None = None,
) -> list[dict] | str:
    """Execute a read-only SQL query.

    Only SELECT, SHOW, EXPLAIN, DESCRIBE, DESC, WITH…SELECT,
    VALUES, and TABLE queries are allowed.

    Args:
        query: The SQL query to execute.
        database: Optional database connection name. Defaults to 'default'.
    """
    query = query.strip()
    if not query:
        raise ValueError("Please pass a valid query.")

    if not is_read_only_query(query):
        raise ValueError(
            "Only read-only queries are allowed "
            "(SELECT, SHOW, EXPLAIN, DESCRIBE, DESC, WITH … SELECT)."
        )

    try:
        conn = connections[database] if database else connection

        with conn.cursor() as cursor:
            cursor.execute(query)

            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return rows
            else:
                return "Query executed (no rows returned)."

    except Exception as e:
        raise ValueError(f"Query failed: {e}") from e
