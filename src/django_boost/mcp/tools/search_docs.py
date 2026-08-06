"""
SearchDocs tool — search version-specific Django ecosystem documentation.

Equivalent to Laravel Boost's SearchDocs tool.
Delegates to a hosted API for semantic documentation search.
"""

import json
from typing import Any
from urllib.request import Request, urlopen

from .base import BoostTool


class SearchDocs(BoostTool):
    """Search for up-to-date documentation related to this project.

    Searches Django-ecosystem hosted documentation based on installed packages.
    Use this tool before using other approaches for Django docs.
    """

    name = "search-docs"
    description = (
        "Search for up-to-date version-specific documentation related to "
        "this project and its packages. This tool searches hosted documentation "
        "based on the packages installed and covers Django, DRF, pytest, "
        "and other Django-ecosystem packages. You must use this tool to "
        "search for Django-ecosystem docs before using other approaches."
    )
    is_read_only = True

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of search queries. Pass multiple if unsure (e.g. 'toggle' vs 'switch').",
                },
                "packages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Package names to limit search to (e.g. 'django', 'djangorestframework').",
                },
                "token_limit": {
                    "type": "integer",
                    "description": "Maximum tokens to return (default: 3000, max: 1000000).",
                },
            },
            "required": ["queries"],
        }

    async def call(self, arguments: dict) -> list[dict]:
        from django.conf import settings

        queries = self._resolve_array(arguments.get("queries", []))
        if isinstance(queries, str):  # Error response
            return self._error(queries)

        packages_filter = self._resolve_array(arguments.get("packages"))
        if isinstance(packages_filter, str):
            return self._error(packages_filter)

        queries = [q.strip() for q in queries if q.strip()]
        if not queries:
            return self._error("Please provide at least one search query.")

        token_limit = min(arguments.get("token_limit", 3000), 1000000)

        # Build package list
        packages = self._get_packages(packages_filter)

        api_url = getattr(
            settings,
            "BOOST_HOSTED_API_URL",
            "https://boost.laravel.com",
        ) + "/api/docs"

        payload = {
            "queries": queries,
            "packages": packages,
            "token_limit": token_limit,
            "format": "markdown",
        }

        try:
            req = Request(
                api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/markdown",
                },
                method="POST",
            )
            with urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8")
                return self._ok(body)
        except Exception as e:
            return self._error(f"Failed to search documentation: {e}")

    def _resolve_array(self, value: Any) -> list | str:
        """Resolve a value that might be a JSON string into a list."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                decoded = json.loads(value)
                if isinstance(decoded, list):
                    return decoded
                return "Invalid parameter: expected a JSON array."
            except json.JSONDecodeError:
                return f"Invalid parameter: {value}"
        if value is None:
            return []
        return str(value)

    def _get_packages(self, package_filter: list | None) -> list[dict]:
        """Get installed packages with versions."""
        from importlib.metadata import packages_distributions, version

        packages = []
        try:
            for dist in sorted(packages_distributions()):
                if package_filter and dist not in package_filter:
                    continue
                try:
                    pkg_version = version(dist)
                    packages.append({"name": dist, "version": pkg_version})
                except Exception:
                    pass
        except Exception:
            pass
        return packages
