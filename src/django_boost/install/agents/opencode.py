"""
OpenCode agent integration.

Equivalent to Laravel Boost's OpenCode agent.
"""

from ...contracts import SupportsGuidelines, SupportsSkills, SupportsMcp
from ..enums.platform import Platform
from .agent import Agent
from .registry import register_agent


@register_agent
class OpenCodeAgent(Agent, SupportsGuidelines, SupportsSkills, SupportsMcp):
    """OpenCode agent."""

    def name(self) -> str:
        return "opencode"

    def display_name(self) -> str:
        return "OpenCode"

    def system_detection_config(self, platform: Platform) -> dict:
        if platform in (Platform.DARWIN, Platform.LINUX):
            return {"command": "which opencode"}
        return {"command": "cmd /c where opencode 2>nul"}

    def project_detection_config(self) -> dict:
        return {"files": ["opencode.jsonc"]}

    def guidelines_path(self) -> str:
        return "AGENTS.md"

    def skills_path(self) -> str:
        return ".opencode/skills"

    def mcp_config_path(self) -> str | None:
        return "opencode.jsonc"
