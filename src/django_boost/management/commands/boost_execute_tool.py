"""
boost:execute-tool — Execute a single MCP tool from the command line.

Usage: python manage.py boost:execute-tool <tool-name> [--args '{"key":"value"}']
"""

import json

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Execute a Django Boost MCP tool from the command line"

    def add_arguments(self, parser):
        parser.add_argument("tool", help="Tool name (e.g., 'database-schema')")
        parser.add_argument("--args", default="{}", help="JSON arguments for the tool")

    def handle(self, **options):
        import asyncio

        tool_name = options["tool"]

        try:
            args = json.loads(options["args"])
        except json.JSONDecodeError as e:
            self.stderr.write(f"Invalid JSON args: {e}")
            return

        self.stdout.write(f"Executing tool: {tool_name}")
        if args:
            self.stdout.write(f"  Arguments: {json.dumps(args)}")

        from django_boost.mcp.server import mcp

        try:
            result = asyncio.run(mcp.call_tool(tool_name, args))
            for item in result if isinstance(result, list) else [result]:
                if hasattr(item, "text"):
                    self.stdout.write(item.text)
                elif isinstance(item, dict) and "text" in item:
                    self.stdout.write(item["text"])
                elif isinstance(item, str):
                    self.stdout.write(item)
            return
        except Exception as e:
            self.stderr.write(f"Error: {e}")
