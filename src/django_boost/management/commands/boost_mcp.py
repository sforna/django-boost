"""
boost:mcp — Start the Django Boost MCP server.

Usage: python manage.py boost:mcp
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start the Django Boost MCP server"

    def handle(self, **options):
        self.stdout.write(self.style.SUCCESS("Starting Django Boost MCP server..."))

        import django
        django.setup()

        from django_boost.mcp.server import mcp

        try:
            mcp.run()
        except KeyboardInterrupt:
            self.stdout.write("\nMCP server stopped.")
