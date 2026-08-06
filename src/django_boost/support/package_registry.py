"""
Package registry — maps pip package names to display names.

Equivalent to Laravel Boost's PackageRegistry.
"""

# Well-known Django ecosystem packages and their display names
_KNOWN_PACKAGES: dict[str, str] = {
    "django": "django",
    "djangorestframework": "djangorestframework",
    "django-ninja": "django-ninja",
    "pytest": "pytest",
    "pytest-django": "pytest-django",
    "celery": "celery",
    "django-celery-results": "django-celery-results",
    "django-allauth": "django-allauth",
    "django-crispy-forms": "django-crispy-forms",
    "django-filter": "django-filter",
    "django-cors-headers": "django-cors-headers",
    "django-storages": "django-storages",
    "django-debug-toolbar": "django-debug-toolbar",
    "django-extensions": "django-extensions",
    "django-htmx": "django-htmx",
    "django-unicorn": "django-unicorn",
    "django-inertia": "django-inertia",
    "whitenoise": "whitenoise",
    "gunicorn": "gunicorn",
    "uvicorn": "uvicorn",
    "psycopg2": "psycopg2",
    "psycopg2-binary": "psycopg2-binary",
    "channels": "channels",
    "django-redis": "django-redis",
    "ruff": "ruff",
    "black": "black",
    "mypy": "mypy",
    "django-stubs": "django-stubs",
}


def roster_name(package_name: str) -> str:
    """Get the display/roster name for a package."""
    return _KNOWN_PACKAGES.get(package_name, package_name)


def is_known(package_name: str) -> bool:
    """Check if a package is in the known registry."""
    return package_name in _KNOWN_PACKAGES
