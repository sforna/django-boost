"""
boost:mcp — Start the Django Boost MCP server.

Usage: python manage.py boost:mcp
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start the Django Boost MCP server"

    def handle(self, **options):
        self.stdout.write(self.style.SUCCESS("Starting Django Boost MCP server..."))

        # Need Django setup before starting the server
        import django

        django.setup()

        import asyncio

        from django_boost.mcp.server import run_server

        try:
            asyncio.run(run_server())
        except KeyboardInterrupt:
            self.stdout.write("\nMCP server stopped.")
