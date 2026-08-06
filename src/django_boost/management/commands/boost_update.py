"""
boost:update — Update existing guidelines, skills, and MCP configuration.

Usage: python manage.py boost:update
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Update Django Boost guidelines, skills, and MCP configuration"

    def add_arguments(self, parser):
        parser.add_argument("--guidelines", action="store_true", help="Update AI guidelines only")
        parser.add_argument("--skills", action="store_true", help="Update agent skills only")
        parser.add_argument("--mcp", action="store_true", help="Update MCP server configuration only")
        parser.add_argument("--yes", action="store_true", help="Skip confirmation prompts")

    def handle(self, **options):
        self.stdout.write(self.style.SUCCESS("Django Boost Update"))
        self.stdout.write("Checking for updates to guidelines, skills, and MCP config...")

        # Detect current configuration
        self._check_project_state()

        # Re-run install with existing configuration
        update_all = not any([options["guidelines"], options["skills"], options["mcp"]])

        if update_all or options["guidelines"]:
            self.stdout.write("  Updating AI guidelines...")
            self._update_guidelines()

        if update_all or options["skills"]:
            self.stdout.write("  Updating agent skills...")
            self._update_skills()

        if update_all or options["mcp"]:
            self.stdout.write("  Updating MCP server configuration...")
            self._update_mcp()

        self.stdout.write(self.style.SUCCESS("Update complete."))

    def _check_project_state(self):
        """Check what's currently installed."""
        import os

        if os.path.isfile("AGENTS.md"):
            with open("AGENTS.md") as f:
                if "django-boost-guidelines" in f.read():
                    self.stdout.write("  Found existing guidelines in AGENTS.md")

    def _update_guidelines(self):
        """Re-run guideline installation."""
        from django_boost.install.guideline_composer import GuidelineComposer

        composer = GuidelineComposer()
        guidelines = composer.compose()
        self.stdout.write(f"  Composed {len(guidelines)} chars of guidelines")

    def _update_skills(self):
        """Re-sync skills."""
        self.stdout.write("  Skills sync (stub — full sync coming soon)")

    def _update_mcp(self):
        """Re-install MCP configuration."""
        self.stdout.write("  MCP config update (stub — full update coming soon)")
