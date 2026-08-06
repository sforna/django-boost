"""
DatabaseSchema tool — reads the database schema for this application.

Equivalent to Laravel Boost's DatabaseSchema tool.
"""

from typing import Any

from ..base import BoostTool
from .factory import SchemaDriverFactory


class DatabaseSchema(BoostTool):
    """Read the database schema for this application.

    Returns table names, columns, indexes, and foreign keys.
    Use "summary" mode first to get an overview, then call again with
    a "filter" to get full details for specific tables.
    """

    name = "database-schema"
    description = (
        "Read the database schema for this application. Returns table names, "
        "columns, indexes, and foreign keys. Use 'summary' first to get an "
        "overview (table names with column types only), then call again "
        "without 'summary' and with a 'filter' to get full details for "
        "specific tables."
    )
    is_read_only = True

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "boolean",
                    "description": "Return only table names and column types. Defaults to false.",
                },
                "filter": {
                    "type": "string",
                    "description": "Filter tables by name (substring match).",
                },
                "include_views": {
                    "type": "boolean",
                    "description": "Include database views. Defaults to false.",
                },
                "include_routines": {
                    "type": "boolean",
                    "description": (
                        "Include stored procedures, functions, and sequences. Defaults to false."
                    ),
                },
                "include_column_details": {
                    "type": "boolean",
                    "description": (
                        "Include full column metadata "
                        "(nullable, default, auto_increment, comments). Defaults to false."
                    ),
                },
            },
        }

    async def call(self, arguments: dict) -> list[dict]:
        summary = arguments.get("summary", False)
        table_filter = arguments.get("filter", "")
        include_views = arguments.get("include_views", False)
        include_routines = arguments.get("include_routines", False)
        include_column_details = arguments.get("include_column_details", False)

        driver = SchemaDriverFactory.make()

        try:
            result: dict[str, Any] = {
                "engine": self._get_engine(),
                "tables": self._get_tables(driver, summary, table_filter, include_column_details),
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
            return self._error(f"Failed to get database structure: {e}")

        return self._json(result)

    def _get_engine(self) -> str:
        from django.db import connection

        return connection.vendor

    def _get_tables(
        self,
        driver,
        summary: bool,
        table_filter: str,
        include_column_details: bool,
    ) -> dict[str, dict]:
        tables = {}
        all_tables = driver.get_tables()

        for table_name in all_tables:
            if table_filter and table_filter.lower() not in table_name.lower():
                continue

            if summary:
                columns = driver.get_columns(table_name)
                tables[table_name] = {col: info.get("type", "unknown") for col, info in columns.items()}
            else:
                tables[table_name] = self._get_table_structure(
                    driver, table_name, include_column_details
                )

        return tables

    def _get_table_structure(
        self,
        driver,
        table_name: str,
        include_column_details: bool,
    ) -> dict:
        try:
            return {
                "columns": self._format_columns(driver.get_columns(table_name), include_column_details),
                "indexes": driver.get_indexes(table_name),
                "foreign_keys": driver.get_foreign_keys(table_name),
                "triggers": driver.get_triggers(table_name),
                "check_constraints": driver.get_check_constraints(table_name),
            }
        except Exception as e:
            return {"error": f"Failed to get structure: {e}"}

    def _format_columns(self, raw_columns: dict, include_details: bool) -> dict[str, dict]:
        if not include_details:
            return {col: {"type": info.get("type", "unknown")} for col, info in raw_columns.items()}
        return raw_columns
