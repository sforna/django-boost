"""
Package registry — known Django-ecosystem packages.

Used by the guideline composer to auto-detect relevant installed packages
and write their versions into AGENTS.md / CLAUDE.md.
"""

# ---------------------------------------------------------------------------
# Packages considered part of the Django ecosystem for guideline injection.
# When one of these is found among the installed packages, its name and
# version are written into the agent guidelines.
# ---------------------------------------------------------------------------
DJANGO_ECOSYSTEM_PACKAGES: frozenset[str] = frozenset({
    # Django core
    "django",
    "djangorestframework",
    "django-ninja",
    # Database / ORM
    "psycopg2",
    "psycopg",
    "psycopg2-binary",
    "mysqlclient",
    "django-model-utils",
    "django-polymorphic",
    # Auth
    "django-allauth",
    "django-guardian",
    "djangorestframework-simplejwt",
    "djangorestframework-api-key",
    # Forms / UI
    "django-crispy-forms",
    "crispy-bootstrap5",
    "crispy-tailwind",
    "django-filter",
    "django-tables2",
    "django-widget-tweaks",
    "django-ckeditor",
    # Admin
    "django-import-export",
    "django-admin-interface",
    "django-jazzmin",
    "django-unfold",
    # Frontend
    "django-htmx",
    "django-unicorn",
    "django-tailwind",
    "django-browser-reload",
    # Tasks / Queues
    "celery",
    "django-celery-beat",
    "django-celery-results",
    "django-q2",
    "django-rq",
    "huey",
    # Channels / WebSockets
    "channels",
    "daphne",
    # Storage / Static
    "django-storages",
    "whitenoise",
    "django-compressor",
    # Cache / Session
    "django-redis",
    "redis",
    # Config
    "django-environ",
    "python-dotenv",
    # Debug / Dev
    "django-debug-toolbar",
    "django-extensions",
    "django-silk",
    "werkzeug",
    "django-browser-reload",
    # CORS / Security
    "django-cors-headers",
    "django-axes",
    # Tagging
    "django-taggit",
    # Sentry / Monitoring
    "sentry-sdk",
    "structlog",
    # Testing
    "pytest",
    "pytest-django",
    "pytest-cov",
    "pytest-xdist",
    "pytest-mock",
    "pytest-factoryboy",
    "model-bakery",
    "factory-boy",
    "faker",
    "coverage",
    "tox",
    "nox",
    # Linting / Formatting
    "ruff",
    "mypy",
    "django-stubs",
    "bandit",
    "pre-commit",
    # HTTP
    "requests",
    "httpx",
    # Deployment
    "gunicorn",
    "uvicorn",
    # Serialization
    "pydantic",
    "marshmallow",
    "drf-spectacular",
    "drf-yasg",
    # CLI / UI
    "rich",
    "typer",
    "click",
    # Misc
    "jinja2",
    "pyyaml",
    "pillow",
    "python-magic",
    "django-csp",
    "icalendar",
    "markdown",
    "django-markdownify",
    "django-mptt",
    "django-treebeard",
    # Build
    "build",
    "hatchling",
    "setuptools",
})
