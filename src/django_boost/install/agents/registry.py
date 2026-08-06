"""
Agent registry — manages all registered AI coding agents.

Equivalent to Laravel Boost's BoostManager.getAgents().
"""

from typing import Type

_registered_agents: list[Type] = []


def register_agent(agent_cls: Type) -> Type:
    """Decorator to register an agent class."""
    _registered_agents.append(agent_cls)
    return agent_cls


def get_registered_agents() -> list[Type]:
    """Return all registered agent classes."""
    return list(_registered_agents)
