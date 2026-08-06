"""
Contracts (interfaces) for agent integrations.

Equivalent to Laravel Boost's Contracts.
"""


class SupportsGuidelines:
    """Agent can receive AI guidelines."""

    def guidelines_path(self) -> str:
        """File path where AI guidelines should be written."""
        raise NotImplementedError

    def frontmatter(self) -> bool:
        """Whether the guideline file requires YAML frontmatter."""
        return False

    def transform_guidelines(self, markdown: str) -> str:
        """Post-process guidelines markdown."""
        return markdown


class SupportsSkills:
    """Agent supports agent skills directories."""

    def skills_path(self) -> str:
        """Directory path where agent skills should be written."""
        raise NotImplementedError


class SupportsMcp:
    """Agent supports MCP (Model Context Protocol)."""

    def use_absolute_path_for_mcp(self) -> bool:
        """Whether to use absolute paths in MCP commands."""
        return False

    def get_python_path(self, force_absolute: bool = False) -> str:
        """Get the Python executable path for MCP."""
        import sys
        return sys.executable if force_absolute else "python"

    def get_manage_py_path(self, force_absolute: bool = False) -> str:
        """Get the manage.py path for MCP."""
        return "manage.py"

    def install_mcp(
        self,
        key: str,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> bool:
        """Install an MCP server configuration."""
        raise NotImplementedError

    def install_http_mcp(self, key: str, url: str) -> bool:
        """Install an HTTP MCP server configuration."""
        raise NotImplementedError
