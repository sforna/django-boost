"""
Base driver for database schema introspection.

Each database backend (SQLite, PostgreSQL, MySQL) implements this interface.
"""

from abc import ABC, abstractmethod


class SchemaDriver(ABC):
    """Abstract base class for database schema drivers."""

    @abstractmethod
    def get_tables(self) -> list[str]:
        """Return all table names."""
        ...

    @abstractmethod
    def get_views(self) -> list[dict]:
        """Return all views."""
        ...

    @abstractmethod
    def get_columns(self, table_name: str) -> dict[str, dict]:
        """Return column info for a table: {col_name: {type, nullable, default, ...}}."""
        ...

    @abstractmethod
    def get_indexes(self, table_name: str) -> dict[str, dict]:
        """Return indexes for a table."""
        ...

    @abstractmethod
    def get_foreign_keys(self, table_name: str) -> list[dict]:
        """Return foreign keys for a table."""
        ...

    def get_triggers(self, table_name: str) -> list[str]:
        """Return trigger names for a table (default: empty)."""
        return []

    def get_check_constraints(self, table_name: str) -> list[dict]:
        """Return check constraints for a table (default: empty)."""
        return []

    def get_stored_procedures(self) -> list[str]:
        """Return stored procedures (default: empty)."""
        return []

    def get_functions(self) -> list[str]:
        """Return functions (default: empty)."""
        return []

    def get_sequences(self) -> list[str]:
        """Return sequences (default: empty)."""
        return []


class NullSchemaDriver(SchemaDriver):
    """Fallback driver when database engine is unsupported."""

    def get_tables(self) -> list[str]:
        return []

    def get_views(self) -> list[dict]:
        return []

    def get_columns(self, table_name: str) -> dict[str, dict]:
        return {}

    def get_indexes(self, table_name: str) -> dict[str, dict]:
        return {}

    def get_foreign_keys(self, table_name: str) -> list[dict]:
        return []
