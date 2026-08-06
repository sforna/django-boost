# Django Boost 🚀

Django Boost accelerates AI-assisted development by providing the essential context and structure that AI needs to generate high-quality, Django-specific code.

> Inspired by [Laravel Boost](https://github.com/laravel/boost) — brought to the Django ecosystem.

## Features (in development)

- **MCP Server** — Django database schema, logs, and tools exposed via Model Context Protocol
- **AI Guidelines** — Curated guidelines for Django, pytest, HTMX, and more
- **Agent Skills** — Auto-install skills for Pi, Cursor, Copilot, and other AI agents
- **Browser Logger** — Capture JS console errors for AI debugging context

## Installation

```
pip install django-boost
```

Add `django_boost` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_boost',
]
```

## Quick Start

```bash
# Install AI guidelines and skills
python manage.py boost:install

# Start the MCP server
python manage.py boost:mcp
```

## Configuration

All settings via Django's `settings.py` with `BOOST_` prefix:

```python
BOOST_ENABLED = True
BOOST_BROWSER_LOGS_WATCHER = True
BOOST_RULES_ENABLED = True
BOOST_TINKER_TOOL_ENABLED = False  # disabled by default for safety
```

## License

MIT
