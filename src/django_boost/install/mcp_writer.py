"""
McpWriter — installs MCP server configuration for agents.

Equivalent to Laravel Boost's McpWriter.
"""

from typing import Any


class McpWriter:
    """Installs MCP server configuration into agent config files."""

    def __init__(self, agent: Any, base_path: str | None = None):
        """Initialize with an agent that supports MCP.

        Args:
            agent: An object with install_mcp() or install_http_mcp() methods
                   and get_python_path() / get_manage_py_path() methods.
            base_path: Optional path to the project root.
        """
        self._agent = agent
        self._base_path = base_path

    def write(
        self,
        sail: Any | None = None,
        nightwatch: Any | None = None,
    ) -> int:
        """Install the Boost MCP server for this agent.

        Returns the number of MCP servers installed (0 or 1).
        """
        key = "django-boost"

        if sail:
            # Sail/Docker: use 'python manage.py boost:mcp'
            command = f"{sail.get_command()} python"
            args = ["manage.py", "boost:mcp"]
            env = sail.get_env() if hasattr(sail, "get_env") else {}
            success = self._agent.install_mcp(key, command, args, env)
        else:
            # Default: use Python from PATH with manage.py
            command = self._agent.get_python_path()
            args = [self._agent.get_manage_py_path(), "boost:mcp"]
            success = self._agent.install_mcp(key, command, args)

        return 1 if success else 0
