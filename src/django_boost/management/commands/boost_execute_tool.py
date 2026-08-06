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
        tool_name = options["tool"]

        try:
            args = json.loads(options["args"])
        except json.JSONDecodeError as e:
            self.stderr.write(f"Invalid JSON args: {e}")
            return

        self.stdout.write(f"Executing tool: {tool_name}")
        if args:
            self.stdout.write(f"  Arguments: {json.dumps(args)}")

        from django_boost.mcp.server import create_server

        try:
            server = create_server()
            # Find the tool
            for tool in server._tools:
                if tool.name == tool_name:
                    import asyncio

                    result = asyncio.run(tool.call(args))
                    for item in result:
                        if item["type"] == "text":
                            self.stdout.write(item["text"])
                    return

            self.stderr.write(f"Tool not found: {tool_name}")
            self.stdout.write(f"Available: {[t.name for t in server._tools]}")

        except Exception as e:
            self.stderr.write(f"Error: {e}")
