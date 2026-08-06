"""
AgentsDetector — discovers installed AI agents on system and project.

Equivalent to Laravel Boost's AgentsDetector.
"""

from .agents.agent import Agent
from .agents.registry import get_registered_agents
from .detection.factory import DetectionStrategyFactory
from .enums.platform import Platform


class AgentsDetector:
    """Detects installed AI coding agents on the current system and project."""

    def __init__(self, strategy_factory: DetectionStrategyFactory | None = None):
        self._strategy_factory = strategy_factory or DetectionStrategyFactory()

    def discover_system_installed_agents(self) -> list[str]:
        """Detect agents installed system-wide on the current platform."""
        platform = Platform.current()
        names = []

        for agent_cls in get_registered_agents():
            agent = agent_cls(self._strategy_factory)
            if agent.detect_on_system(platform):
                names.append(agent.name())

        return names

    def discover_project_installed_agents(self, base_path: str) -> list[str]:
        """Detect agents used in the current project."""
        names = []

        for agent_cls in get_registered_agents():
            agent = agent_cls(self._strategy_factory)
            if agent.detect_in_project(base_path):
                names.append(agent.name())

        return names

    def get_agents(self) -> dict[str, Agent]:
        """Get all registered agents as {name: instance}."""
        agents = {}
        for agent_cls in get_registered_agents():
            instance = agent_cls(self._strategy_factory)
            agents[instance.name()] = instance
        return agents
