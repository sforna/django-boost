"""
GuidelineAssist — provides template helper functions for guideline rendering.

Equivalent to Laravel Boost's GuidelineAssist.
"""

import sys
from importlib.metadata import packages_distributions, version

from .package_registry import DJANGO_ECOSYSTEM_PACKAGES


class GuidelineAssist:
    """Provides helper methods available to guideline Jinja2 templates.

    In templates, this object is available as `assist`:
        {{ assist.python_version() }}
        {{ assist.manage_py_command('migrate') }}
    """

    def __init__(self):
        self._has_skills = False

    def set_skills_enabled(self, enabled: bool) -> None:
        self._has_skills = enabled

    def python_version(self) -> str:
        """Return the current Python version string."""
        return f"{sys.version_info.major}.{sys.version_info.minor}"

    def django_version(self) -> str:
        """Return the Django version string."""
        import django

        return django.get_version()

    def manage_py_command(self, cmd: str) -> str:
        """Format a manage.py command for display.

        Args:
            cmd: The management command (e.g., 'migrate', 'test').

        Returns:
            A code-formatted string like `python manage.py migrate`.
        """
        return f"`python manage.py {cmd}`"

    def artisan_command(self, cmd: str) -> str:
        """Alias for manage_py_command (compatibility with Laravel templates)."""
        return self.manage_py_command(cmd)

    def node_package_manager_command(self, cmd: str) -> str:
        """Format an npm/yarn command for display."""
        return f"`npm {cmd}`"

    def composer_command(self, cmd: str) -> str:
        """Format a pip/composer command for display."""
        return f"`pip {cmd}`"

    def has_skills_enabled(self) -> bool:
        """Check if skills are enabled."""
        return self._has_skills

    def bootstrap_version(self) -> str | None:
        """Detect Bootstrap version if installed."""
        try:
            import json

            with open("package.json") as f:
                data = json.load(f)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "bootstrap" in deps:
                return deps["bootstrap"].lstrip("^~")
        except Exception:
            pass
        return None

    def get_database_engine(self) -> str:
        """Return the configured database engine."""
        from django.conf import settings

        engine = settings.DATABASES.get("default", {}).get("ENGINE", "unknown")
        short_map = {
            "django.db.backends.sqlite3": "sqlite",
            "django.db.backends.postgresql": "postgresql",
            "django.db.backends.mysql": "mysql",
        }
        return short_map.get(engine, engine)

    def key_packages(self) -> list[dict[str, str]]:
        """Return installed Django-ecosystem packages with versions.

        Scans all installed packages and returns those that are part
        of the Django ecosystem, sorted alphabetically. Each entry has
        'name' and 'version' keys.
        """
        packages: list[dict[str, str]] = []
        try:
            for dist in sorted(packages_distributions()):
                # Only include known Django-ecosystem packages
                if dist not in DJANGO_ECOSYSTEM_PACKAGES:
                    continue
                try:
                    packages.append(
                        {
                            "name": dist,
                            "version": version(dist),
                        }
                    )
                except Exception:
                    pass
        except Exception:
            pass
        return packages
