"""
Schema driver factory — creates the appropriate driver for the active database.
"""

from django.db import connection

from .base import NullSchemaDriver, SchemaDriver
from .mysql import MySQLSchemaDriver
from .postgresql import PostgreSQLSchemaDriver
from .sqlite import SQLiteSchemaDriver


class SchemaDriverFactory:
    """Factory that creates the correct SchemaDriver for the database backend."""

    _drivers = {
        "sqlite": SQLiteSchemaDriver,
        "postgresql": PostgreSQLSchemaDriver,
        "mysql": MySQLSchemaDriver,
    }

    @classmethod
    def make(cls) -> SchemaDriver:
        """Create and return the appropriate schema driver."""
        engine = connection.vendor
        driver_cls = cls._drivers.get(engine, NullSchemaDriver)
        return driver_cls()
