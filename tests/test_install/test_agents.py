"""
Tests for agent integrations.
"""

import pytest

from django_boost.install.agents.agent import Agent
from django_boost.install.agents.registry import get_registered_agents
from django_boost.install.agents_detector import AgentsDetector
from django_boost.install.detection.factory import DetectionStrategyFactory
from django_boost.install.enums.platform import Platform


class TestAgentRegistry:
    """Tests for the agent registry."""

    def test_agents_are_registered(self):
        """All built-in agents should be self-registered."""
        # Trigger imports via apps.ready()
        from django_boost.apps import DjangoBoostConfig
        # Import triggers the @register_agent decorators
        from django_boost.install.agents import (
            amp, claude_code, codex, copilot, cursor,
            grok_build, opencode, pi, zed,
        )

        agents = get_registered_agents()
        assert len(agents) >= 9  # At least the 9 built-in agents

    def test_agent_names_are_unique(self):
        """Each agent should have a unique name."""
        from django_boost.install.agents import (
            pi, cursor, copilot, codex, claude_code,
            zed, amp, opencode, grok_build,
        )

        factory = DetectionStrategyFactory()
        names = []
        for cls in [pi.PiAgent, cursor.CursorAgent, copilot.CopilotAgent,
                     codex.CodexAgent, claude_code.ClaudeCodeAgent,
                     zed.ZedAgent, amp.AmpAgent, opencode.OpenCodeAgent,
                     grok_build.GrokBuildAgent]:
            agent = cls(factory)
            names.append(agent.name())

        assert len(names) == len(set(names)), f"Duplicate names: {names}"


class TestPiAgent:
    """Tests for the Pi agent."""

    def test_name(self):
        from django_boost.install.agents.pi import PiAgent
        agent = PiAgent(DetectionStrategyFactory())
        assert agent.name() == "pi"

    def test_display_name(self):
        from django_boost.install.agents.pi import PiAgent
        agent = PiAgent(DetectionStrategyFactory())
        assert agent.display_name() == "Pi"

    def test_guidelines_path(self):
        from django_boost.install.agents.pi import PiAgent
        agent = PiAgent(DetectionStrategyFactory())
        assert agent.guidelines_path() == "AGENTS.md"

    def test_skills_path(self):
        from django_boost.install.agents.pi import PiAgent
        agent = PiAgent(DetectionStrategyFactory())
        assert ".pi/skills" in agent.skills_path()

    def test_project_detection_checks_pi_directory(self, tmp_path):
        from django_boost.install.agents.pi import PiAgent
        agent = PiAgent(DetectionStrategyFactory())

        pi_dir = tmp_path / ".pi"
        pi_dir.mkdir()
        (pi_dir / "settings.json").write_text("{}")

        assert agent.detect_in_project(str(tmp_path)) is True

    def test_project_detection_negative(self, tmp_path):
        from django_boost.install.agents.pi import PiAgent
        agent = PiAgent(DetectionStrategyFactory())
        assert agent.detect_in_project(str(tmp_path)) is False


class TestClaudeCode:
    """Tests for the Claude Code agent."""

    def test_name(self):
        from django_boost.install.agents.claude_code import ClaudeCodeAgent
        agent = ClaudeCodeAgent(DetectionStrategyFactory())
        assert agent.name() == "claude-code"

    def test_guidelines_path_is_claude_md(self):
        from django_boost.install.agents.claude_code import ClaudeCodeAgent
        agent = ClaudeCodeAgent(DetectionStrategyFactory())
        assert agent.guidelines_path() == "CLAUDE.md"

    def test_mcp_supports_absolute_paths(self):
        from django_boost.install.agents.claude_code import ClaudeCodeAgent
        agent = ClaudeCodeAgent(DetectionStrategyFactory())
        assert agent.use_absolute_path_for_mcp() is True


class TestAgentsDetector:
    """Tests for AgentsDetector."""

    def test_get_agents_returns_dict(self):
        from django_boost.install.agents import pi, cursor
        detector = AgentsDetector()
        agents = detector.get_agents()
        assert isinstance(agents, dict)
        assert "pi" in agents
        assert "cursor" in agents

    def test_discover_project_installed(self, tmp_path):
        from django_boost.install.agents.pi import PiAgent

        # Create a .pi directory so Pi is detected
        pi_dir = tmp_path / ".pi"
        pi_dir.mkdir()
        (pi_dir / "settings.json").write_text("{}")

        detector = AgentsDetector()
        agents = detector.discover_project_installed_agents(str(tmp_path))
        assert "pi" in agents
