"""
Tests for the command normalizer.
"""

import pytest

from django_boost.support.command_normalizer import normalize_command


class TestNormalizeCommand:
    """Tests for normalize_command()."""

    def test_simple_command(self):
        """A single-word command should not be split."""
        result = normalize_command("python")
        assert result["command"] == "python"
        assert result["args"] == []

    def test_command_with_args(self):
        """Space-separated parts become args."""
        result = normalize_command("python manage.py boost:mcp")
        assert result["command"] == "python"
        assert result["args"] == ["manage.py", "boost:mcp"]

    def test_absolute_path_kept_intact(self):
        """Absolute paths with spaces should not be split."""
        result = normalize_command("/usr/bin/my script")
        # Absolute path: kept as-is
        assert result["command"] == "/usr/bin/my script"
        assert result["args"] == []

    def test_extra_args_appended(self):
        """Extra args should be appended after parsed args."""
        result = normalize_command("python manage.py test", ["--keepdb"])
        assert result["command"] == "python"
        assert result["args"] == ["manage.py", "test", "--keepdb"]

    def test_quoted_strings_preserved(self):
        """Quoted strings should be split correctly."""
        result = normalize_command('python -c "print(1)"')
        assert result["command"] == "python"
        assert result["args"] == ["-c", "print(1)"]
