"""
Grok Build agent integration (xAI).

Equivalent to Laravel Boost's GrokBuild agent.
"""

import os

from ...contracts import SupportsGuidelines, SupportsSkills, SupportsMcp
from ..enums.platform import Platform
from .agent import Agent
from .registry import register_agent


@register_agent
class GrokBuildAgent(Agent, SupportsGuidelines, SupportsSkills, SupportsMcp):
    """xAI Grok Build agent."""

    def name(self) -> str:
        return "grok-build"

    def display_name(self) -> str:
        return "Grok Build"

    def system_detection_config(self, platform: Platform) -> dict:
        home = os.path.expanduser("~")
        return {"paths": [
            os.path.join(home, ".grok"),
        ]}

    def project_detection_config(self) -> dict:
        return {"paths": [".grok"]}

    def guidelines_path(self) -> str:
        return ".grok/AGENTS.md"

    def skills_path(self) -> str:
        return ".grok/skills"

    def mcp_config_path(self) -> str | None:
        return ".grok/mcp.json"
