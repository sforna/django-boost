from django.apps import AppConfig


class DjangoBoostConfig(AppConfig):
    """Django Boost application configuration.

    Registers MCP server, middleware, and management commands.
    """

    name = "django_boost"
    verbose_name = "Django Boost"

    def ready(self) -> None:
        """Called when Django starts. Registers routes and browser logger."""
        self._register_mcp()
        self._configure_browser_logging()

    def _register_mcp(self) -> None:
        """Register the Django Boost MCP server."""
        # MCP server is started via management command, not auto-started.
        # We only need to ensure the tools are importable.
        pass

    def _configure_browser_logging(self) -> None:
        """Configure browser log channel if not already defined."""
        from django.conf import settings

        if not hasattr(settings, "LOGGING") or "browser" not in settings.LOGGING.get("loggers", {}):
            # Browser logging is configured via settings, not forced by the app.
            pass
