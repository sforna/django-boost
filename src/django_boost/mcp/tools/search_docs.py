"""
SearchDocs tool — look up version-specific Django ecosystem documentation.

Generates direct documentation links for installed packages using version-aware
URL patterns (inspired by django-ai-boost's documentation prompt).
"""

from __future__ import annotations

import json
from importlib.metadata import packages_distributions, version

from django_boost.mcp.server import mcp

# ---------------------------------------------------------------------------
# Known documentation URL patterns for the Django ecosystem.
# {major} and {minor} are extracted from the installed package version.
# ---------------------------------------------------------------------------
KNOWN_DOC_URLS: dict[str, str] = {
    "django": "https://docs.djangoproject.com/en/{major}.{minor}/",
    "djangorestframework": "https://www.django-rest-framework.org/",
    "pytest": "https://docs.pytest.org/en/{major}.{minor}/",
    "pytest-django": "https://pytest-django.readthedocs.io/en/latest/",
    "pytest-cov": "https://pytest-cov.readthedocs.io/en/latest/",
    "pytest-xdist": "https://pytest-xdist.readthedocs.io/en/latest/",
    "celery": "https://docs.celeryq.dev/en/{major}.{minor}/",
    "django-celery-beat": "https://django-celery-beat.readthedocs.io/en/latest/",
    "django-celery-results": "https://django-celery-results.readthedocs.io/en/latest/",
    "django-debug-toolbar": "https://django-debug-toolbar.readthedocs.io/en/latest/",
    "django-extensions": "https://django-extensions.readthedocs.io/en/latest/",
    "django-filter": "https://django-filter.readthedocs.io/en/stable/",
    "django-cors-headers": "https://github.com/adamchainz/django-cors-headers#readme",
    "django-allauth": "https://docs.allauth.org/en/latest/",
    "django-storages": "https://django-storages.readthedocs.io/en/latest/",
    "django-redis": "https://github.com/jazzband/django-redis#readme",
    "django-compressor": "https://django-compressor.readthedocs.io/en/latest/",
    "django-crispy-forms": "https://django-crispy-forms.readthedocs.io/en/latest/",
    "django-taggit": "https://django-taggit.readthedocs.io/en/latest/",
    "django-htmx": "https://django-htmx.readthedocs.io/en/latest/",
    "django-model-utils": "https://django-model-utils.readthedocs.io/en/latest/",
    "django-guardian": "https://django-guardian.readthedocs.io/en/stable/",
    "django-polymorphic": "https://django-polymorphic.readthedocs.io/en/stable/",
    "django-ckeditor": "https://django-ckeditor.readthedocs.io/en/latest/",
    "django-import-export": "https://django-import-export.readthedocs.io/en/latest/",
    "django-tables2": "https://django-tables2.readthedocs.io/en/latest/",
    "django-widget-tweaks": "https://github.com/jazzband/django-widget-tweaks#readme",
    "django-environ": "https://django-environ.readthedocs.io/en/latest/",
    "channels": "https://channels.readthedocs.io/en/stable/",
    "daphne": "https://github.com/django/daphne#readme",
    "uvicorn": "https://www.uvicorn.org/",
    "gunicorn": "https://docs.gunicorn.org/en/stable/",
    "psycopg2": "https://www.psycopg.org/docs/",
    "psycopg": "https://www.psycopg.org/psycopg3/docs/",
    "mysqlclient": "https://mysqlclient.readthedocs.io/en/latest/",
    "pillow": "https://pillow.readthedocs.io/en/stable/",
    "requests": "https://docs.python-requests.org/en/latest/",
    "httpx": "https://www.python-httpx.org/",
    "redis": "https://redis-py.readthedocs.io/en/stable/",
    "python-dotenv": "https://github.com/theskumar/python-dotenv#readme",
    "whitenoise": "http://whitenoise.evans.io/en/stable/",
    "sentry-sdk": "https://docs.sentry.io/platforms/python/",
    "structlog": "https://www.structlog.org/en/stable/",
    "rich": "https://rich.readthedocs.io/en/stable/",
    "pydantic": "https://docs.pydantic.dev/latest/",
    "marshmallow": "https://marshmallow.readthedocs.io/en/stable/",
    "factory-boy": "https://factoryboy.readthedocs.io/en/stable/",
    "faker": "https://faker.readthedocs.io/en/stable/",
    "coverage": "https://coverage.readthedocs.io/en/stable/",
    "pre-commit": "https://pre-commit.com/",
    "ruff": "https://docs.astral.sh/ruff/",
    "jinja2": "https://jinja.palletsprojects.com/en/{major}.{minor}.x/",
    "pyyaml": "https://pyyaml.org/wiki/PyYAMLDocumentation",
    "mypy": "https://mypy.readthedocs.io/en/stable/",
    "bandit": "https://bandit.readthedocs.io/en/latest/",
    "ipython": "https://ipython.readthedocs.io/en/stable/",
    "bpython": "https://docs.bpython-interpreter.org/en/latest/",
    "django-ninja": "https://django-ninja.dev/",
    "django-stubs": "https://github.com/typeddjango/django-stubs#readme",
    "types-requests": "https://github.com/python/typeshed",
    "selenium": "https://www.selenium.dev/documentation/",
    "playwright": "https://playwright.dev/python/",
    "model-bakery": "https://model-bakery.readthedocs.io/en/latest/",
    "tox": "https://tox.wiki/en/latest/",
    "nox": "https://nox.thea.codes/en/stable/",
    "build": "https://build.pypa.io/en/stable/",
}


def _build_version_url(pkg_name: str, pkg_version: str) -> str | None:
    """Build a documentation URL for a known package using its version."""
    if pkg_name not in KNOWN_DOC_URLS:
        return None

    template = KNOWN_DOC_URLS[pkg_name]
    parts = pkg_version.split(".")

    major = parts[0] if len(parts) > 0 else "0"
    minor = parts[1] if len(parts) > 1 else "0"

    return template.format(major=major, minor=minor)


def _collect_packages(filter_list: list[str] | None = None) -> list[dict]:
    """Collect installed packages with versions and doc URLs."""
    pkg_list: list[dict] = []
    try:
        for dist in sorted(packages_distributions()):
            if filter_list and dist not in filter_list:
                continue
            try:
                pkg_version = version(dist)
                entry: dict = {"name": dist, "version": pkg_version}
                doc_url = _build_version_url(dist, pkg_version)
                if doc_url:
                    entry["docs_url"] = doc_url
                pkg_list.append(entry)
            except Exception:
                pass
    except Exception:
        pass
    return pkg_list


@mcp.tool(
    name="search-docs",
    description=(
        "Look up version-specific documentation for Django-ecosystem packages. "
        "Returns direct documentation links based on installed packages and "
        "their exact versions. For Django itself, generates search URLs for "
        "each query pointing to the correct documentation version. "
        "Use this tool to discover relevant documentation before browsing manually."
    ),
    annotations={"readOnlyHint": True},
)
def search_docs(
    queries: list[str],
    packages: list[str] | None = None,
) -> str:
    """Look up Django ecosystem documentation links.

    Generates version-aware documentation URLs for the installed packages
    matching the given queries, plus direct Django docs search links.

    Args:
        queries: List of search topics (e.g. 'queryset annotate', 'ModelAdmin').
        packages: Optional package names to focus on
                  (e.g. 'django', 'djangorestframework').
    """
    # ------------------------------------------------------------------
    # Normalise query input
    # ------------------------------------------------------------------
    if isinstance(queries, str):
        try:
            queries = json.loads(queries)
        except json.JSONDecodeError:
            raise ValueError("Invalid queries: expected a JSON array.")

    queries = [q.strip() for q in queries if q.strip()]
    if not queries:
        raise ValueError("Please provide at least one search query.")

    # ------------------------------------------------------------------
    # Collect installed packages with version info
    # ------------------------------------------------------------------
    pkg_list = _collect_packages(filter_list=packages)

    # ------------------------------------------------------------------
    # Build the response
    # ------------------------------------------------------------------
    django_pkg = next((p for p in pkg_list if p["name"] == "django"), None)
    pkgs_with_docs = [p for p in pkg_list if "docs_url" in p]

    lines: list[str] = []

    # -- Django version banner -------------------------------------------------
    if django_pkg:
        major = django_pkg["version"].split(".")[0]
        minor = django_pkg["version"].split(".")[1] if "." in django_pkg["version"] else "0"
        lines.append(
            f"**Django {django_pkg['version']}** — "
            f"docs: https://docs.djangoproject.com/en/{major}.{minor}/"
        )
    else:
        lines.append("**Django not detected** among installed packages.")
    lines.append("")

    # -- Query-specific Django search links ------------------------------------
    if django_pkg and queries:
        major = django_pkg["version"].split(".")[0]
        minor = django_pkg["version"].split(".")[1] if "." in django_pkg["version"] else "0"
        lines.append("### Search Django documentation")
        lines.append("")
        for q in queries:
            encoded = q.replace(" ", "+")
            lines.append(
                f"- [{q}](https://docs.djangoproject.com/en/{major}.{minor}/search/?q={encoded})"
            )
        lines.append("")

    # -- Related package docs --------------------------------------------------
    if pkgs_with_docs:
        lines.append("### Related package documentation")
        lines.append("")
        seen: set[str] = set()
        for pkg in pkgs_with_docs:
            if pkg is django_pkg:
                continue
            url = pkg["docs_url"]
            if url not in seen:
                seen.add(url)
                lines.append(f"- **{pkg['name']}** ({pkg['version']}): {url}")
        lines.append("")

    # -- Django key reference links --------------------------------------------
    if django_pkg:
        major = django_pkg["version"].split(".")[0]
        minor = django_pkg["version"].split(".")[1] if "." in django_pkg["version"] else "0"
        base = f"https://docs.djangoproject.com/en/{major}.{minor}"
        lines.append("### Django reference")
        lines.append("")
        lines.append(f"- [Topic guides]({base}/topics/)")
        lines.append(f"- [API reference]({base}/ref/)")
        lines.append(f"- [How-to guides]({base}/howto/)")
        lines.append(f"- [General index]({base}/genindex/)")
        lines.append("")

    return "\n".join(lines)
