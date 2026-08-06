"""
Pi agent integration.

Equivalent to Laravel Boost's Pi agent.
"""

from ...contracts import SupportsGuidelines, SupportsSkills
from ..enums.platform import Platform
from .agent import Agent
from .registry import register_agent


@register_agent
class PiAgent(Agent, SupportsGuidelines, SupportsSkills):
    """Pi coding agent by Earendil Works."""

    def name(self) -> str:
        return "pi"

    def display_name(self) -> str:
        return "Pi"

    def system_detection_config(self, platform: Platform) -> dict:
        if platform in (Platform.DARWIN, Platform.LINUX):
            return {"command": "which pi"}
        return {"command": "cmd /c where pi 2>nul"}

    def project_detection_config(self) -> dict:
        return {
            "paths": [".pi"],
            "files": [".pi/settings.json"],
        }

    def guidelines_path(self) -> str:
        from django.conf import settings
        return getattr(settings, "BOOST_AGENTS", {}).get(
            "pi", {}
        ).get("guidelines_path", "AGENTS.md")

    def skills_path(self) -> str:
        from django.conf import settings
        return getattr(settings, "BOOST_AGENTS", {}).get(
            "pi", {}
        ).get("skills_path", ".pi/skills")
