"""
ApplicationInfo tool — returns comprehensive application metadata.
"""

import sys
from importlib.metadata import packages_distributions, version

import django

from django_boost.mcp.server import mcp


@mcp.tool(
    name="application-info",
    description=(
        "Get comprehensive application information including Python version, "
        "Django version, database engine, and all installed packages with their "
        "versions. Use this tool on each new chat, and use the package & version "
        "data to write version-specific code for the packages that exist."
    ),
    annotations={"readOnlyHint": True},
)
def application_info() -> dict:
    """Return application metadata as a dictionary."""
    from django.conf import settings

    db_config = settings.DATABASES.get("default", {})
    return {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "django_version": django.get_version(),
        "database_engine": db_config.get("ENGINE", "unknown"),
        "packages": _get_packages(),
    }


def _get_packages() -> list[dict[str, str]]:
    """Get installed Python packages with versions."""
    packages: list[dict[str, str]] = []
    try:
        for dist in sorted(packages_distributions()):
            try:
                packages.append({"name": dist, "version": version(dist)})
            except Exception:
                pass
    except Exception:
        pass
    return packages
