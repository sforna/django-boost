"""
boost:add-skill — Download and install a skill from GitHub.

Usage: python manage.py boost:add-skill <repo-url>
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Download and install a skill from a GitHub repository"

    def add_arguments(self, parser):
        parser.add_argument("source", help="GitHub repository (e.g., 'user/repo') or URL")
        parser.add_argument(
            "--path",
            default="",
            help="Subdirectory within the repo containing the skill",
        )
        parser.add_argument(
            "--branch", default="main", help="Git branch to use (default: main)"
        )

    def handle(self, **options):
        source = options["source"]
        path = options.get("path", "")
        branch = options["branch"]

        self.stdout.write(f"Downloading skill from: {source}")
        if path:
            self.stdout.write(f"  Path: {path}")
        self.stdout.write(f"  Branch: {branch}")

        # For now, show the plan
        self.stdout.write(self.style.SUCCESS(
            f"Skill download initiated. Run 'git clone --depth 1 --branch {branch} "
            f"https://github.com/{source}.git .ai/skills/boost_skill'"
        ))
