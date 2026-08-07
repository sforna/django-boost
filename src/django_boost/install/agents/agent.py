"""
Base Agent class for AI coding assistant integrations.

Equivalent to Laravel Boost's abstract Agent class.
"""

import json
import os
import re
import subprocess
from abc import ABC, abstractmethod
from typing import Any

from ..detection.factory import DetectionStrategyFactory
from ..enums.mcp_installation_strategy import McpInstallationStrategy
from ..enums.platform import Platform


class Agent(ABC):
    """Abstract base for AI agent integrations.

    Subclasses define agent-specific paths, detection configs,
    and MCP installation strategies.
    """

    def __init__(self, strategy_factory: DetectionStrategyFactory):
        self._strategy_factory = strategy_factory

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    @abstractmethod
    def name(self) -> str:
        """Unique agent identifier (e.g., 'pi', 'cursor')."""
        ...

    @abstractmethod
    def display_name(self) -> str:
        """Human-readable display name."""
        ...

    @abstractmethod
    def system_detection_config(self, platform: Platform) -> dict:
        """Detection config for system-wide installation check.

        Returns a dict that may contain:
        - 'command': shell command to run
        - 'paths': list of directories to check
        - 'files': list of files to check
        """
        ...

    @abstractmethod
    def project_detection_config(self) -> dict:
        """Detection config for project-specific check.

        Returns a dict that may contain:
        - 'paths': list of relative directories to check
        - 'files': list of relative files to check
        """
        ...

    # ------------------------------------------------------------------
    # MCP support
    # ------------------------------------------------------------------

    def use_absolute_path_for_mcp(self) -> bool:
        """Whether to use absolute paths in MCP config."""
        return False

    def get_python_path(self, force_absolute: bool = False) -> str:
        """Get the Python executable path for MCP commands."""
        from django.conf import settings

        config_path = getattr(settings, "BOOST_EXECUTABLE_PATHS", {}).get("python")
        if config_path:
            return config_path

        if self.use_absolute_path_for_mcp() or force_absolute:
            return self._get_absolute_python_path()

        return "python"

    def _get_absolute_python_path(self) -> str:
        import sys

        return sys.executable

    def get_manage_py_path(self, force_absolute: bool = False) -> str:
        """Get the manage.py path for MCP commands."""
        return "manage.py"

    def mcp_installation_strategy(self) -> McpInstallationStrategy:
        """How to install MCP config for this agent."""
        return McpInstallationStrategy.FILE

    def shell_mcp_command(self) -> str | None:
        """Shell command template for agents using SHELL strategy."""
        return None

    def mcp_config_path(self) -> str | None:
        """Path to the agent's MCP config file."""
        return None

    def mcp_config_key(self) -> str:
        """The JSON key for MCP servers in the config file."""
        return "mcpServers"

    def default_mcp_config(self) -> dict[str, Any]:
        """Default values for the MCP config file."""
        return {}

    def frontmatter(self) -> bool:
        """Whether guidelines file uses YAML frontmatter."""
        return False

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def detect_on_system(self, platform: Platform) -> bool:
        """Check if the agent is installed system-wide."""
        config = self.system_detection_config(platform)
        strategy = self._strategy_factory.make_from_config(config)
        return strategy.detect(config, platform)

    def detect_in_project(self, base_path: str) -> bool:
        """Check if the agent is used in this project."""
        config = {**self.project_detection_config(), "basePath": base_path}
        strategy = self._strategy_factory.make_from_config(config)
        return strategy.detect(config)

    # ------------------------------------------------------------------
    # MCP Installation
    # ------------------------------------------------------------------

    def install_mcp(
        self,
        key: str,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> bool:
        """Install MCP server configuration for this agent."""
        args = args or []
        env = env or {}
        strategy = self.mcp_installation_strategy()

        if strategy == McpInstallationStrategy.SHELL:
            return self._install_shell_mcp(key, command, args, env)
        elif strategy == McpInstallationStrategy.FILE:
            return self._install_file_mcp(key, command, args, env)
        return False

    def http_mcp_server_config(self, url: str) -> dict[str, Any]:
        """Build HTTP MCP server config payload."""
        return {"type": "http", "url": url}

    def install_http_mcp(self, key: str, url: str) -> bool:
        """Install an HTTP MCP server config."""
        path = self.mcp_config_path()
        if not path:
            return False
        return self._write_mcp_config(path, key, self.http_mcp_server_config(url))

    def mcp_server_config(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Build stdio MCP server config payload."""
        config: dict[str, Any] = {
            "command": command,
            "args": args or [],
        }
        if env:
            config["env"] = env
        return config

    def _install_shell_mcp(
        self,
        key: str,
        command: str,
        args: list[str],
        env: dict[str, str],
    ) -> bool:
        """Install MCP via shell command."""
        shell_template = self.shell_mcp_command()
        if not shell_template:
            return False

        normalized = self._normalize_command(command, args)
        env_str = " ".join(f'-e {k.upper()}="{v}"' for k, v in env.items())

        cmd = shell_template.format(
            key=key,
            command=normalized["command"],
            args=" ".join(f'"{a}"' for a in normalized["args"]),
            env=env_str,
        )

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)  # nosec B602
            if result.returncode == 0:
                return True
            return "already exists" in result.stderr.decode(errors="replace")
        except Exception:
            return False

    def _install_file_mcp(
        self,
        key: str,
        command: str,
        args: list[str],
        env: dict[str, str],
    ) -> bool:
        """Install MCP via config file."""
        path = self.mcp_config_path()
        if not path:
            return False

        normalized = self._normalize_command(command, args)
        config = self.mcp_server_config(normalized["command"], normalized["args"], env if env else None)
        return self._write_mcp_config(path, key, config)

    def _write_mcp_config(self, path: str, key: str, server_config: dict) -> bool:
        """Write or update an MCP server entry in a JSON/TOML config file."""
        full_path = os.path.join(os.getcwd(), path)

        # Read existing config
        existing: dict[str, Any] = {}
        if os.path.isfile(full_path):
            try:
                with open(full_path, "r") as f:
                    existing = json.load(f)
            except json.JSONDecodeError:
                existing = {}

        # Initialize with defaults
        if not existing:
            existing = self.default_mcp_config()

        # Update the MCP servers entry
        mcp_key = self.mcp_config_key()
        if mcp_key not in existing:
            existing[mcp_key] = {}
        existing[mcp_key][key] = server_config

        # Write back
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            json.dump(existing, f, indent=2)

        return True

    def _normalize_command(self, command: str, args: list[str] | None = None) -> dict[str, Any]:
        """Normalize a command by splitting space-separated parts.

        Absolute paths with spaces are kept intact.
        """
        args = args or []

        # If the command looks like an absolute path, don't split
        if command.startswith("/") or re.match(r"^[A-Za-z]:\\", command):
            return {"command": command, "args": args}

        # Split by spaces, preserving quoted strings
        parts = re.findall(r'"[^"]*"|\'[^\']*\'|\S+', command.strip())
        parts = [p.strip("\"'") for p in parts]

        if len(parts) > 1:
            return {"command": parts[0], "args": parts[1:] + args}

        return {"command": command, "args": args}

    # ------------------------------------------------------------------
    # Guidelines
    # ------------------------------------------------------------------

    def transform_guidelines(self, markdown: str) -> str:
        """Post-process generated guidelines markdown."""
        return markdown

    @classmethod
    def from_name(cls, name: str) -> "Agent | None":
        """Look up an agent by name from registered agents."""
        from .registry import get_registered_agents

        agents = get_registered_agents()
        for agent_cls in agents:
            factory = DetectionStrategyFactory()
            instance = agent_cls(factory)
            if instance.name() == name:
                return instance
        return None
