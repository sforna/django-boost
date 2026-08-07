"""
DatabaseSchema tool — reads the database schema for this application.
"""

from django_boost.mcp.server import mcp
from .factory import SchemaDriverFactory


@mcp.tool(
    name="database-schema",
    description=(
        "Read the database schema for this application. Returns table names, "
        "columns, indexes, and foreign keys. Use 'summary' first to get an "
        "overview (table names with column types only), then call again "
        "without 'summary' and with a 'filter' to get full details for "
        "specific tables."
    ),
    annotations={"readOnlyHint": True},
)
def database_schema(
    summary: bool = False,
    filter: str = "",
    include_views: bool = False,
    include_routines: bool = False,
    include_column_details: bool = False,
) -> dict:
    """Read the full database schema.

    Args:
        summary: Return only table names and column types. Defaults to false.
        filter: Filter tables by name (substring match).
        include_views: Include database views. Defaults to false.
        include_routines: Include stored procedures, functions, and sequences.
        include_column_details: Include full column metadata (nullable, default, etc.).
    """
    from django.db import connection

    driver = SchemaDriverFactory.make()

    try:
        result: dict = {
            "engine": connection.vendor,
            "tables": _get_tables(driver, summary, filter, include_column_details),
        }

        if not summary:
            if include_views:
                result["views"] = driver.get_views()
            if include_routines:
                result["routines"] = {
                    "stored_procedures": driver.get_stored_procedures(),
                    "functions": driver.get_functions(),
                    "sequences": driver.get_sequences(),
                }
    except Exception as e:
        raise ValueError(f"Failed to get database structure: {e}") from e

    return result


def _get_tables(
    driver,
    summary: bool,
    table_filter: str,
    include_column_details: bool,
) -> dict[str, dict]:
    tables: dict[str, dict] = {}
    all_tables = driver.get_tables()

    for table_name in all_tables:
        if table_filter and table_filter.lower() not in table_name.lower():
            continue

        if summary:
            columns = driver.get_columns(table_name)
            tables[table_name] = {
                col: info.get("type", "unknown") for col, info in columns.items()
            }
        else:
            tables[table_name] = _get_table_structure(driver, table_name, include_column_details)

    return tables


def _get_table_structure(driver, table_name: str, include_column_details: bool) -> dict:
    try:
        return {
            "columns": _format_columns(driver.get_columns(table_name), include_column_details),
            "indexes": driver.get_indexes(table_name),
            "foreign_keys": driver.get_foreign_keys(table_name),
            "triggers": driver.get_triggers(table_name),
            "check_constraints": driver.get_check_constraints(table_name),
        }
    except Exception as e:
        return {"error": f"Failed to get structure: {e}"}


def _format_columns(raw_columns: dict, include_details: bool) -> dict[str, dict]:
    if not include_details:
        return {col: {"type": info.get("type", "unknown")} for col, info in raw_columns.items()}
    return raw_columns
