"""
PostgreSQL schema driver.
"""

from django.db import connection

from .base import SchemaDriver


class PostgreSQLSchemaDriver(SchemaDriver):
    """Schema driver for PostgreSQL databases."""

    def get_tables(self) -> list[str]:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT tablename FROM pg_catalog.pg_tables "
                "WHERE schemaname NOT IN ('pg_catalog', 'information_schema') "
                "ORDER BY tablename"
            )
            return [row[0] for row in cursor.fetchall()]

    def get_views(self) -> list[dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT table_name, view_definition "
                "FROM information_schema.views "
                "WHERE table_schema NOT IN ('pg_catalog', 'information_schema') "
                "ORDER BY table_name"
            )
            return [{"name": row[0], "definition": row[1]} for row in cursor.fetchall()]

    def get_columns(self, table_name: str) -> dict[str, dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT column_name, data_type, is_nullable, column_default "
                "FROM information_schema.columns "
                "WHERE table_name = %s "
                "ORDER BY ordinal_position",
                [table_name],
            )
            columns = {}
            for row in cursor.fetchall():
                columns[row[0]] = {
                    "type": row[1] or "unknown",
                    "nullable": row[2] == "YES",
                    "default": row[3],
                }
            return columns

    def get_indexes(self, table_name: str) -> dict[str, dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT indexname, indexdef FROM pg_catalog.pg_indexes WHERE tablename = %s",
                [table_name],
            )
            indexes = {}
            for row in cursor.fetchall():
                is_unique = "UNIQUE" in row[1].upper()
                is_primary = "PRIMARY" in row[1].upper()
                indexes[row[0]] = {
                    "columns": [],
                    "definition": row[1],
                    "is_unique": is_unique,
                    "is_primary": is_primary,
                }
            return indexes

    def get_foreign_keys(self, table_name: str) -> list[dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "  kcu.column_name, "
                "  ccu.table_name AS references_table, "
                "  ccu.column_name AS references_column "
                "FROM information_schema.table_constraints tc "
                "JOIN information_schema.key_column_usage kcu "
                "  ON tc.constraint_name = kcu.constraint_name "
                "JOIN information_schema.constraint_column_usage ccu "
                "  ON ccu.constraint_name = tc.constraint_name "
                "WHERE tc.constraint_type = 'FOREIGN KEY' "
                "  AND tc.table_name = %s",
                [table_name],
            )
            return [
                {
                    "column": row[0],
                    "references_table": row[1],
                    "references_column": row[2],
                }
                for row in cursor.fetchall()
            ]

    def get_sequences(self) -> list[str]:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT sequence_name FROM information_schema.sequences ORDER BY sequence_name"
            )
            return [row[0] for row in cursor.fetchall()]
