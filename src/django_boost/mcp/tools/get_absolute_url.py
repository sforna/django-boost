"""
GetAbsoluteUrl tool — converts a relative path to an absolute URL.

Equivalent to Laravel Boost's GetAbsoluteUrl tool.
"""

from typing import Any

from .base import BoostTool


class GetAbsoluteUrl(BoostTool):
    """Get the absolute URL for a given relative path or named route.

    If no arguments are provided, returns the absolute URL for "/".
    """

    name = "get-absolute-url"
    description = (
        "Get the absolute URL for a given relative path or named route. "
        'If no arguments are provided, returns the absolute URL for "/".'
    )
    is_read_only = True

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": 'The relative URL/path (e.g. "/dashboard") to convert to an absolute URL.',
                },
                "route": {
                    "type": "string",
                    "description": 'The named route to generate an absolute URL for (e.g. "home").',
                },
            },
        }

    async def call(self, arguments: dict) -> list[dict]:
        from django.conf import settings
        from django.urls import reverse

        path = arguments.get("path")
        route_name = arguments.get("route")

        # Determine the base URL
        base_url = getattr(settings, "BOOST_BASE_URL", None)
        if not base_url:
            base_url = f"http://localhost:8000"

        if path:
            return self._ok(f"{base_url.rstrip('/')}{path}")

        if route_name:
            try:
                resolved = reverse(route_name)
                return self._ok(f"{base_url.rstrip('/')}{resolved}")
            except Exception as e:
                return self._error(f"Failed to resolve route '{route_name}': {e}")

        return self._ok(base_url)
