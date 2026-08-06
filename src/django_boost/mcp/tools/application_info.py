"""
ApplicationInfo tool — returns comprehensive application metadata.

Equivalent to Laravel Boost's ApplicationInfo tool.
"""

import sys
from importlib.metadata import packages_distributions, version

import django

from .base import BoostTool


class ApplicationInfo(BoostTool):
    """Get comprehensive application information.

    Returns Python version, Django version, database engine,
    and all installed packages with their versions.
    """

    name = "application-info"
    description = (
        "Get comprehensive application information including Python version, "
        "Django version, database engine, and all installed packages with their "
        "versions. Use this tool on each new chat, and use the package & version "
        "data to write version-specific code for the packages that exist."
    )
    is_read_only = True

    async def call(self, arguments: dict) -> list[dict]:
        from django.conf import settings

        db_config = settings.DATABASES.get("default", {})
        return self._json({
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "django_version": django.get_version(),
            "database_engine": db_config.get("ENGINE", "unknown"),
            "packages": self._get_packages(),
        })

    def _get_packages(self) -> list[dict[str, str]]:
        """Get installed Python packages with versions."""
        packages = []
        try:
            for dist in sorted(packages_distributions()):
                try:
                    pkg_version = version(dist)
                    packages.append({
                        "name": dist,
                        "version": pkg_version,
                    })
                except Exception:
                    pass
        except Exception:
            pass
        return packages
