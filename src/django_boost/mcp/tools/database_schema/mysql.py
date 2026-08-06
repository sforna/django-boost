"""
MySQL schema driver.
"""

from django.db import connection

from .base import SchemaDriver


class MySQLSchemaDriver(SchemaDriver):
    """Schema driver for MySQL databases."""

    def get_tables(self) -> list[str]:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            return [row[0] for row in cursor.fetchall()]

    def get_views(self) -> list[dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT TABLE_NAME, VIEW_DEFINITION "
                "FROM INFORMATION_SCHEMA.VIEWS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "ORDER BY TABLE_NAME"
            )
            return [{"name": row[0], "definition": row[1]} for row in cursor.fetchall()]

    def get_columns(self, table_name: str) -> dict[str, dict]:
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
            columns = {}
            for row in cursor.fetchall():
                # Field, Type, Null, Key, Default, Extra
                columns[row[0]] = {
                    "type": row[1] or "unknown",
                    "nullable": row[2] == "YES",
                    "default": row[4],
                    "auto_increment": "auto_increment" in (row[5] or ""),
                }
            return columns

    def get_indexes(self, table_name: str) -> dict[str, dict]:
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW INDEX FROM `{table_name}`")
            indexes: dict[str, dict] = {}
            for row in cursor.fetchall():
                # Table, Non_unique, Key_name, Seq_in_index, Column_name, ...
                idx_name = row[2]
                if idx_name not in indexes:
                    indexes[idx_name] = {
                        "columns": [],
                        "is_unique": not row[1],
                        "is_primary": idx_name == "PRIMARY",
                    }
                indexes[idx_name]["columns"].append(row[4])
            return indexes

    def get_foreign_keys(self, table_name: str) -> list[dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
                "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "  AND TABLE_NAME = %s "
                "  AND REFERENCED_TABLE_NAME IS NOT NULL",
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

    def get_stored_procedures(self) -> list[str]:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES "
                "WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'PROCEDURE' "
                "ORDER BY ROUTINE_NAME"
            )
            return [row[0] for row in cursor.fetchall()]

    def get_functions(self) -> list[str]:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES "
                "WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'FUNCTION' "
                "ORDER BY ROUTINE_NAME"
            )
            return [row[0] for row in cursor.fetchall()]
