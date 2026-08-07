"""
SearchDocs tool — search version-specific Django ecosystem documentation.

Delegates to a hosted API for semantic documentation search.
"""

import json
from importlib.metadata import packages_distributions, version
from urllib.request import Request, urlopen

from django_boost.mcp.server import mcp


@mcp.tool(
    name="search-docs",
    description=(
        "Search for up-to-date version-specific documentation related to "
        "this project and its packages. This tool searches hosted documentation "
        "based on the packages installed and covers Django, DRF, pytest, "
        "and other Django-ecosystem packages. You must use this tool to "
        "search for Django-ecosystem docs before using other approaches."
    ),
    annotations={"readOnlyHint": True},
)
def search_docs(
    queries: list[str],
    packages: list[str] | None = None,
    token_limit: int = 3000,
) -> str:
    """Search Django ecosystem documentation.

    Args:
        queries: List of search queries. Pass multiple if unsure (e.g. 'toggle' vs 'switch').
        packages: Package names to limit search to (e.g. 'django', 'djangorestframework').
        token_limit: Maximum tokens to return (default: 3000, max: 1000000).
    """
    from django.conf import settings

    if isinstance(queries, str):
        try:
            queries = json.loads(queries)
        except json.JSONDecodeError:
            raise ValueError("Invalid queries: expected a JSON array.")

    queries = [q.strip() for q in queries if q.strip()]
    if not queries:
        raise ValueError("Please provide at least one search query.")

    token_limit = min(token_limit, 1000000)

    # Build package list
    pkg_list: list[dict] = []
    try:
        for dist in sorted(packages_distributions()):
            if packages and dist not in packages:
                continue
            try:
                pkg_list.append({"name": dist, "version": version(dist)})
            except Exception:
                pass
    except Exception:
        pass

    api_url = (
        getattr(settings, "BOOST_HOSTED_API_URL", "https://boost.laravel.com")
        + "/api/docs"
    )

    payload = {
        "queries": queries,
        "packages": pkg_list,
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
            return resp.read().decode("utf-8")
    except Exception as e:
        raise ValueError(f"Failed to search documentation: {e}") from e
