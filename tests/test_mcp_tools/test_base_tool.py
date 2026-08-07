"""
Tests for MCP tools — verifies they are registered and callable via FastMCP.
"""

import asyncio

import pytest

from django_boost.mcp.server import mcp


class TestMCPTools:
    """Verify all tools are properly registered on the FastMCP instance."""

    def test_all_expected_tools_registered(self):
        """Should have the 11 standard tools registered."""
        tools_list = asyncio.run(mcp.list_tools())
        tool_names = {t.name for t in tools_list}

        expected = {
            "application-info",
            "browser-logs",
            "database-connections",
            "database-query",
            "database-schema",
            "get-absolute-url",
            "last-error",
            "read-log-entries",
            "record-rule",
            "search-docs",
            "tinker",
        }
        assert tool_names == expected

    def test_application_info_returns_dict(self):
        """application-info should return structured content."""
        result = asyncio.run(mcp.call_tool("application-info", {}))
        assert not result.is_error
        assert result.structured_content is not None
        assert "python_version" in result.structured_content
        assert "django_version" in result.structured_content


class TestDatabaseSchemaTool:
    """Tests for the database-schema tool."""

    @pytest.mark.django_db
    def test_summary_mode(self):
        """Should return summary with table names and column types."""
        result = asyncio.run(
            mcp.call_tool("database-schema", {"summary": True})
        )
        assert not result.is_error
        text = result.content[0].text
        assert "sqlite" in text.lower()


class TestDatabaseConnectionsTool:
    """Tests for the database-connections tool."""

    def test_returns_connections(self):
        """Should return a list of connections."""
        result = asyncio.run(mcp.call_tool("database-connections", {}))
        assert not result.is_error
        text = result.content[0].text
        assert "default" in text.lower()


class TestRecordRuleTool:
    """Tests for the record-rule tool."""

    def test_missing_args_raises(self):
        """Should raise an error when required args are missing."""
        with pytest.raises(Exception):
            asyncio.run(
                mcp.call_tool("record-rule", {"glob": "", "title": "", "note": ""})
            )


class TestTinkerTool:
    """Tests for the tinker tool."""

    def test_disabled_by_default(self):
        """Should fail because tinker is disabled in test settings."""
        with pytest.raises(Exception):
            asyncio.run(mcp.call_tool("tinker", {"code": "1 + 1"}))


class TestGetAbsoluteUrlTool:
    """Tests for the get-absolute-url tool."""

    def test_default_url(self):
        """Should return default localhost URL when no args given."""
        result = asyncio.run(mcp.call_tool("get-absolute-url", {}))
        assert not result.is_error
        text = result.content[0].text
        assert "localhost" in text


class TestDatabaseQueryTool:
    """Tests for the database-query tool."""

    def test_invalid_query_rejected(self):
        """Should reject write queries."""
        with pytest.raises(Exception):
            asyncio.run(
                mcp.call_tool("database-query", {"query": "DELETE FROM users"})
            )
