"""
boost_install — Interactive installation of Django Boost features.

Usage: python manage.py boost_install
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Install Django Boost guidelines, skills, and MCP configuration"

    def add_arguments(self, parser):
        parser.add_argument("--guidelines", action="store_true", help="Install AI guidelines")
        parser.add_argument("--skills", action="store_true", help="Install agent skills")
        parser.add_argument("--mcp", action="store_true", help="Install MCP server configuration")

    def handle(self, **options):
        self.stdout.write(self.style.SUCCESS("Django Boost Install"))
        self.stdout.write(
            "This command will configure AI guidelines, skills, and MCP servers for your Django project."
        )
        self.stdout.write("(Full installation wizard coming in a future version.)")

        # For now, just acknowledge which features were requested
        features = []
        if options["guidelines"]:
            features.append("guidelines")
        if options["skills"]:
            features.append("skills")
        if options["mcp"]:
            features.append("mcp")

        if features:
            self.stdout.write(f"Selected features: {', '.join(features)}")
        else:
            self.stdout.write("No features selected. Use --guidelines, --skills, or --mcp.")
