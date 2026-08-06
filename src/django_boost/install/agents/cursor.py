"""
Cursor agent integration.

Equivalent to Laravel Boost's Cursor agent.
"""

import os

from ...contracts import SupportsGuidelines, SupportsSkills
from ..enums.platform import Platform
from .agent import Agent
from .registry import register_agent


@register_agent
class CursorAgent(Agent, SupportsGuidelines, SupportsSkills):
    """Cursor IDE agent."""

    def name(self) -> str:
        return "cursor"

    def display_name(self) -> str:
        return "Cursor"

    def system_detection_config(self, platform: Platform) -> dict:
        if platform == Platform.DARWIN:
            return {
                "paths": [
                    "/Applications/Cursor.app",
                    os.path.expanduser("~/Applications/Cursor.app"),
                ]
            }
        elif platform == Platform.WINDOWS:
            return {"paths": ["C:\\Program Files\\Cursor"]}
        return {"paths": ["/usr/share/cursor"]}

    def project_detection_config(self) -> dict:
        return {"paths": [".cursor", ".cursorrules"], "files": [".cursorrules"]}

    def guidelines_path(self) -> str:
        return ".cursorrules"

    def skills_path(self) -> str:
        return ".cursor/skills"

    def frontmatter(self) -> bool:
        return True
