"""
GetAbsoluteUrl tool — converts a relative path to an absolute URL.
"""

from django_boost.mcp.server import mcp


@mcp.tool(
    name="get-absolute-url",
    description=(
        "Get the absolute URL for a given relative path or named route. "
        'If no arguments are provided, returns the absolute URL for "/".'
    ),
    annotations={"readOnlyHint": True},
)
def get_absolute_url(path: str | None = None, route: str | None = None) -> str:
    """Convert a relative path or named route to an absolute URL."""
    from django.conf import settings
    from django.urls import reverse

    base_url = getattr(settings, "BOOST_BASE_URL", None)
    if not base_url:
        base_url = "http://localhost:8000"

    if path:
        return f"{base_url.rstrip('/')}{path}"

    if route:
        try:
            resolved = reverse(route)
            return f"{base_url.rstrip('/')}{resolved}"
        except Exception as e:
            raise ValueError(f"Failed to resolve route '{route}': {e}") from e

    return base_url
