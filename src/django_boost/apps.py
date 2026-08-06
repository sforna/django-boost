from django.apps import AppConfig


class DjangoBoostConfig(AppConfig):
    """Django Boost application configuration.

    Registers MCP server, middleware, and management commands.
    """

    name = "django_boost"
    verbose_name = "Django Boost"

    def ready(self) -> None:
        """Called when Django starts. Imports agents and registers commands."""
        self._import_agents()

    def _import_agents(self) -> None:
        """Import all agent classes so they self-register."""
        try:
            from .install.agents import (
                pi,
                cursor,
                copilot,
                codex,
                claude_code,
                zed,
                amp,
                opencode,
                grok_build,
            )
        except ImportError:
            pass
