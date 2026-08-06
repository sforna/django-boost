"""
Zed editor agent integration.

Equivalent to Laravel Boost's Zed agent.
"""

from ...contracts import SupportsGuidelines, SupportsSkills, SupportsMcp
from ..enums.platform import Platform
from .agent import Agent
from .registry import register_agent


@register_agent
class ZedAgent(Agent, SupportsGuidelines, SupportsSkills, SupportsMcp):
    """Zed code editor agent."""

    def name(self) -> str:
        return "zed"

    def display_name(self) -> str:
        return "Zed"

    def system_detection_config(self, platform: Platform) -> dict:
        if platform == Platform.DARWIN:
            return {"paths": ["/Applications/Zed.app"]}
        elif platform == Platform.WINDOWS:
            return {"paths": ["C:\\Program Files\\Zed"]}
        return {"paths": ["/usr/share/zed"]}

    def project_detection_config(self) -> dict:
        return {"paths": [".zed"]}

    def guidelines_path(self) -> str:
        return ".zed/AGENTS.md"

    def skills_path(self) -> str:
        return ".zed/skills"

    def mcp_config_path(self) -> str | None:
        return ".zed/mcp.json"

    def use_absolute_path_for_mcp(self) -> bool:
        return True
