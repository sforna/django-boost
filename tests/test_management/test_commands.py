"""
Tests for management commands.
"""

import sys
from io import StringIO

import pytest
from django.core.management import call_command


class TestBoostMcpCommand:
    """Tests for boost:mcp command."""

    def test_command_registered(self):
        """The command can be called without error (though MCP start may fail in tests)."""
        out = StringIO()
        # Just verify command exists and has help
        sys.argv = ["manage.py", "boost:mcp", "--help"]
        # Just check the command is loadable
        from django_boost.management.commands.boost_mcp import Command
        cmd = Command()
        assert cmd.help is not None


class TestBoostInstallCommand:
    """Tests for boost:install command."""

    def test_command_help(self):
        """Should display help text."""
        from django_boost.management.commands.boost_install import Command
        cmd = Command()
        assert cmd.help is not None

    def test_adds_arguments(self):
        """Should accept --guidelines, --skills, --mcp flags."""
        from django_boost.management.commands.boost_install import Command
        from argparse import ArgumentParser
        cmd = Command()
        parser = ArgumentParser()
        cmd.add_arguments(parser)
        args = parser.parse_args(["--guidelines", "--mcp"])
        assert args.guidelines is True
        assert args.mcp is True
        assert args.skills is False


class TestBoostListSkillCommand:
    """Tests for boost:list-skill command."""

    def test_command_exists(self):
        from django_boost.management.commands.boost_list_skill import Command
        cmd = Command()
        assert cmd.help is not None
