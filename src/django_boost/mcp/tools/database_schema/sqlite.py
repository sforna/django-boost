"""
SQLite schema driver.
"""

from django.db import connection

from .base import SchemaDriver


class SQLiteSchemaDriver(SchemaDriver):
    """Schema driver for SQLite databases."""

    def get_tables(self) -> list[str]:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                "AND name NOT LIKE 'django_%' "
                "ORDER BY name"
            )
            return [row[0] for row in cursor.fetchall()]

    def get_views(self) -> list[dict]:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='view' ORDER BY name")
            return [{"name": row[0], "definition": row[1]} for row in cursor.fetchall()]

    def get_columns(self, table_name: str) -> dict[str, dict]:
        with connection.cursor() as cursor:
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            columns = {}
            for row in cursor.fetchall():
                # PRAGMA table_info: cid, name, type, notnull, dflt_value, pk
                columns[row[1]] = {
                    "type": row[2] or "TEXT",
                    "nullable": not row[3],
                    "default": row[4],
                    "auto_increment": bool(row[5]),
                }
            return columns

    def get_indexes(self, table_name: str) -> dict[str, dict]:
        with connection.cursor() as cursor:
            cursor.execute(f"PRAGMA index_list('{table_name}')")
            indexes = {}
            for row in cursor.fetchall():
                # seq, name, unique, origin, partial
                idx_name = row[1]
                cursor.execute(f"PRAGMA index_info('{idx_name}')")
                info_rows = cursor.fetchall()
                cols = [r[2] for r in info_rows] if info_rows else []
                indexes[idx_name] = {
                    "columns": cols,
                    "is_unique": bool(row[2]),
                    "is_primary": idx_name.startswith("sqlite_autoindex"),
                }
            return indexes

    def get_foreign_keys(self, table_name: str) -> list[dict]:
        with connection.cursor() as cursor:
            cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
            return [
                {
                    "column": row[3],
                    "references_table": row[2],
                    "references_column": row[4],
                }
                for row in cursor.fetchall()
            ]
