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
            from .install.agents import (  # noqa: F401
                amp,
                claude_code,
                codex,
                copilot,
                cursor,
                grok_build,
                opencode,
                pi,
                zed,
            )
        except ImportError:
            pass
