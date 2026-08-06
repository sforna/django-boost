"""
Claude Code agent integration.

Equivalent to Laravel Boost's ClaudeCode agent.
"""

import os

from ...contracts import SupportsGuidelines, SupportsSkills, SupportsMcp
from ..enums.platform import Platform
from .agent import Agent
from .registry import register_agent


@register_agent
class ClaudeCodeAgent(Agent, SupportsGuidelines, SupportsSkills, SupportsMcp):
    """Anthropic Claude Code agent."""

    def name(self) -> str:
        return "claude-code"

    def display_name(self) -> str:
        return "Claude Code"

    def system_detection_config(self, platform: Platform) -> dict:
        if platform in (Platform.DARWIN, Platform.LINUX):
            return {"command": "which claude"}
        return {"command": "cmd /c where claude 2>nul"}

    def project_detection_config(self) -> dict:
        return {"paths": [".claude"], "files": [".claude/settings.json"]}

    def guidelines_path(self) -> str:
        return "CLAUDE.md"

    def skills_path(self) -> str:
        return ".claude/skills"

    def mcp_config_path(self) -> str | None:
        return ".claude/mcp.json"

    def use_absolute_path_for_mcp(self) -> bool:
        return True
