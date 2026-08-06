"""
Amp agent integration.

Equivalent to Laravel Boost's Amp agent.
"""

from ...contracts import SupportsGuidelines, SupportsSkills, SupportsMcp
from ..enums.platform import Platform
from .agent import Agent
from .registry import register_agent


@register_agent
class AmpAgent(Agent, SupportsGuidelines, SupportsSkills, SupportsMcp):
    """Amp agent."""

    def name(self) -> str:
        return "amp"

    def display_name(self) -> str:
        return "Amp"

    def system_detection_config(self, platform: Platform) -> dict:
        if platform in (Platform.DARWIN, Platform.LINUX):
            return {"command": "which amp"}
        return {"command": "cmd /c where amp 2>nul"}

    def project_detection_config(self) -> dict:
        return {"paths": [".amp"], "files": [".amp/settings.json"]}

    def guidelines_path(self) -> str:
        return "AGENTS.md"

    def skills_path(self) -> str:
        return ".amp/skills"

    def mcp_config_path(self) -> str | None:
        return ".amp/mcp.json"

    def mcp_config_key(self) -> str:
        return "amp.mcpServers"

    def use_absolute_path_for_mcp(self) -> bool:
        return True
