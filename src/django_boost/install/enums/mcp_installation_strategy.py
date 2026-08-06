"""
MCP installation strategy enum.

Equivalent to Laravel Boost's McpInstallationStrategy.
"""

from enum import Enum


class McpInstallationStrategy(Enum):
    """How to install the MCP server configuration for an agent."""

    FILE = "file"  # Write to a config file (JSON, TOML)
    SHELL = "shell"  # Execute a shell command
    NONE = "none"  # No MCP support
