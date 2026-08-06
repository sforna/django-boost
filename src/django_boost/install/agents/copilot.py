"""
GitHub Copilot agent integration.

Equivalent to Laravel Boost's Copilot agent.
"""

from ...contracts import SupportsGuidelines, SupportsSkills
from ..enums.platform import Platform
from .agent import Agent
from .registry import register_agent


@register_agent
class CopilotAgent(Agent, SupportsGuidelines, SupportsSkills):
    """GitHub Copilot agent."""

    def name(self) -> str:
        return "copilot"

    def display_name(self) -> str:
        return "GitHub Copilot"

    def system_detection_config(self, platform: Platform) -> dict:
        return {"paths": []}  # Detected via editor presence

    def project_detection_config(self) -> dict:
        return {"files": [".github/copilot-instructions.md"]}

    def guidelines_path(self) -> str:
        return ".github/copilot-instructions.md"

    def skills_path(self) -> str:
        return ".github/skills"
