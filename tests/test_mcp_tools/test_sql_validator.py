"""
Tests for the read-only SQL validator.

Port of the security validation from laravel-boost's DatabaseQuery.
"""

import pytest

from django_boost.mcp.tools.sql_validator import is_read_only_query


class TestReadOnlyQuery:
    """Tests for is_read_only_query()."""

    # Allowed queries
    @pytest.mark.parametrize("query", [
        "SELECT * FROM users",
        "SELECT id, name FROM auth_user WHERE is_active = 1",
        "SHOW TABLES",
        "SHOW COLUMNS FROM users",
        "EXPLAIN SELECT * FROM users",
        "DESCRIBE users",
        "DESC users",
        "WITH active AS (SELECT * FROM users WHERE is_active=1) SELECT * FROM active",
        "VALUES (1, 2, 3)",
        "TABLE users",
    ])
    def test_allows_read_only_queries(self, query):
        """Should allow standard read-only queries."""
        assert is_read_only_query(query) is True

    # Blocked queries
    @pytest.mark.parametrize("query", [
        "DELETE FROM users",
        "UPDATE users SET name = 'test'",
        "DROP TABLE users",
        "ALTER TABLE users ADD COLUMN x INT",
        "TRUNCATE users",
        "CREATE TABLE foo (id INT)",
        "INSERT INTO users VALUES (1)",
        "SELECT * FROM users INTO OUTFILE '/tmp/dump'",
        # Stacked statements
        "SELECT * FROM users; DROP TABLE users",
        "SELECT * FROM users; DELETE FROM users",
    ])
    def test_blocks_write_queries(self, query):
        """Should block all write/DDL operations."""
        assert is_read_only_query(query) is False

    def test_allows_insert_as_function_call(self):
        """INSERT(...) used as a function call should be allowed in SELECT."""
        assert is_read_only_query(
            "SELECT INSERT('hello', 1, 0, 'H')"
        ) is True

    def test_blocks_without_select(self):
        """WITH without SELECT should be blocked."""
        assert is_read_only_query("WITH cte AS (DELETE FROM users)") is False

    def test_handles_quoted_strings(self):
        """String literals containing SQL keywords should be ignored."""
        assert is_read_only_query(
            "SELECT * FROM users WHERE note = 'DROP TABLE users'"
        ) is True

    def test_handles_line_comments(self):
        """Line comments should not affect validation."""
        assert is_read_only_query(
            "SELECT * FROM users -- DROP TABLE users"
        ) is True

    def test_handles_block_comments(self):
        """Block comments should not affect validation."""
        assert is_read_only_query(
            "SELECT * FROM /* DELETE FROM users */ users"
        ) is True

    def test_handles_backtick_identifiers(self):
        """Backtick-quoted identifiers should not break validation."""
        assert is_read_only_query(
            "SELECT * FROM `users`"
        ) is True

    def test_empty_query(self):
        """Empty queries should be caught by the caller, not the validator."""
        assert is_read_only_query("") is False
