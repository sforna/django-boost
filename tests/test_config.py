"""
Tests for django_boost.config module.
"""

from django.test import override_settings

from django_boost.config import DEFAULTS, get_config


class TestGetConfig:
    """Tests for get_config() function."""

    def test_returns_default_when_not_configured(self):
        """Should return the default value when no override is set."""
        assert get_config("enabled") == DEFAULTS["enabled"]

    def test_returns_override_from_django_settings(self):
        """Should return the value from Django settings when BOOST_* is set."""
        with override_settings(BOOST_ENABLED=False):
            assert get_config("enabled") is False

    def test_case_insensitive_key(self):
        """Key lookup should be case-insensitive."""
        with override_settings(BOOST_ENABLED=False):
            assert get_config("ENABLED") is False
            assert get_config("Enabled") is False

    def test_browser_log_levels_default(self):
        """Default browser log levels are the 4 standard levels."""
        levels = get_config("browser_log_levels")
        assert isinstance(levels, list)
        assert "error" in levels

    def test_tinker_tool_disabled_by_default(self):
        """Tinker tool should be disabled by default for safety."""
        assert get_config("tinker_tool_enabled") is False

    def test_all_defaults_have_sensible_values(self):
        """All default config keys should be present."""
        assert "enabled" in DEFAULTS
        assert "browser_logs_watcher" in DEFAULTS
        assert "rules_enabled" in DEFAULTS
        assert "mcp_tools_exclude" in DEFAULTS
        assert "mcp_tool_timeout" in DEFAULTS
