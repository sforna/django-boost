"""
Codex agent integration.

Equivalent to Laravel Boost's Codex agent by OpenAI.
"""

from ...contracts import SupportsGuidelines, SupportsMcp, SupportsSkills
from ..enums.platform import Platform
from .agent import Agent
from .registry import register_agent


@register_agent
class CodexAgent(Agent, SupportsGuidelines, SupportsSkills, SupportsMcp):
    """OpenAI Codex agent."""

    def name(self) -> str:
        return "codex"

    def display_name(self) -> str:
        return "Codex"

    def system_detection_config(self, platform: Platform) -> dict:
        if platform in (Platform.DARWIN, Platform.LINUX):
            return {"command": "which codex"}
        return {"command": "cmd /c where codex 2>nul"}

    def project_detection_config(self) -> dict:
        return {"paths": [".codex"], "files": [".codex/config.toml"]}

    def guidelines_path(self) -> str:
        return "CODEX.md"

    def skills_path(self) -> str:
        return ".codex/skills"

    def mcp_config_path(self) -> str | None:
        return ".codex/mcp.json"

    def use_absolute_path_for_mcp(self) -> bool:
        return True
