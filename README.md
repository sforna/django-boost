# Django Boost 🚀

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-4.2%2B-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE.md)
[![Tests](https://img.shields.io/badge/tests-83%20passed-success)](https://github.com/sforna/django-boost/actions)

**Django Boost** accelerates AI-assisted development by providing the essential context and structure that AI coding agents need to generate high-quality, Django-specific code.

> Inspired by [Laravel Boost](https://github.com/laravel/boost) — brought to the Django ecosystem.

---

## What it does

Django Boost gives AI coding agents (like Pi, Cursor, Claude Code, Copilot, and others) deep knowledge of your Django project by exposing:

- **📊 Database Schema** — Full introspected schema: tables, columns, indexes, foreign keys
- **📝 Application Logs** — Backend errors (`last-error`, `read-log-entries`) and browser console logs
- **🔍 Documentation Search** — Semantic search over Django ecosystem docs
- **📏 Project Rules** — Durable, committed rules in `.ai/rules/` shared across your team
- **📋 AI Guidelines** — Curated markdown guidelines for Django, pytest, HTMX, DRF, Celery, and more
- **🔧 Code Execution** — Safe `manage.py shell`-style execution (opt-in)

All exposed through a single **MCP (Model Context Protocol)** server.

---

## Installation

### With pip

```bash
pip install django-boost
```

### With uv (recommended)

```bash
# Add as a dev dependency — NO changes to INSTALLED_APPS required
uv add --dev django-boost
```

### Django project setup

**No changes to your Django project are required.** Django Boost works as a standalone
CLI tool and does not need to be added to `INSTALLED_APPS`.

Just make sure `DJANGO_SETTINGS_MODULE` is set in your environment:

```bash
export DJANGO_SETTINGS_MODULE=myproject.settings
```

> **Optional integrations** — if you want browser console log capture, you can
  optionally add `django_boost` to `INSTALLED_APPS`, include the URLs, and add the
  middleware. These are extras, not requirements.

---

## Quick Start

```bash
# Make sure your Django settings module is set
export DJANGO_SETTINGS_MODULE=myproject.settings

# Interactive setup: guidelines, skills, and MCP config
django-boost install

# Start the MCP server for your AI agent
django-boost mcp
```

Or, if you prefer Django management commands (requires `django_boost` in `INSTALLED_APPS`):

```bash
python manage.py boost_install
python manage.py boost_mcp
```

---

## Supported AI Agents

Django Boost auto-detects and configures these agents:

| Agent | Guidelines | Skills | MCP |
|-------|-----------|--------|-----|
| **Amp** | `AGENTS.md` | `.amp/skills` | ✅ |
| **Claude Code** | `CLAUDE.md` | `.claude/skills` | ✅ |
| **Codex** | `CODEX.md` | `.codex/skills` | ✅ |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `.github/skills` | — |
| **Cursor** | `.cursorrules` | `.cursor/skills` | — |
| **Grok Build** | `.grok/AGENTS.md` | `.grok/skills` | ✅ |
| **OpenCode** | `AGENTS.md` | `.opencode/skills` | ✅ |
| **Pi** | `AGENTS.md` | `.pi/skills` | ✅ |
| **Zed** | `.zed/AGENTS.md` | `.zed/skills` | ✅ |

Run `python manage.py boost_install` and Boost detects which agents you have installed.

---

## MCP Tools

11 tools available to your AI agent:

| Tool | Description |
|------|-------------|
| `application-info` | Python version, Django version, all installed packages |
| `database-schema` | Full schema: tables, columns, indexes, FKs |
| `database-query` | Execute read-only SQL (security-validated) |
| `database-connections` | List configured database connections |
| `last-error` | Get the last backend error from logs |
| `read-log-entries` | Read last N application log entries |
| `browser-logs` | Read browser console logs captured in real-time |
| `get-absolute-url` | Convert relative path to absolute URL |
| `search-docs` | Search Django ecosystem documentation |
| `record-rule` | Write durable project rules to `.ai/rules/` |
| `tinker` | Execute Python code in Django context (disabled by default) |

---

## Management Commands

Django Boost provides both a **standalone CLI** (no `INSTALLED_APPS` required) and
traditional **Django management commands** (requires `django_boost` in `INSTALLED_APPS`).

| Standalone CLI | Management command (optional) | Description |
|---|---|---|
| `django-boost install` | `python manage.py boost_install` | Interactive setup wizard |
| `django-boost update` | `python manage.py boost_update` | Refresh guidelines/skills/MCP config |
| `django-boost mcp` | `python manage.py boost_mcp` | Start the MCP server |
| `django-boost list-skill` | `python manage.py boost_list_skill` | List available skills |
| `django-boost add-skill <repo>` | `python manage.py boost_add_skill <repo>` | Download a skill from GitHub |
| `django-boost execute-tool <tool>` | `python manage.py boost_execute_tool <tool>` | Run a single tool |

```bash
# Standalone usage (recommended — no INSTALLED_APPS needed)
django-boost mcp
django-boost install --guidelines --mcp

# Or via manage.py (if django_boost is in INSTALLED_APPS)
python manage.py boost_mcp
```

---

## Configuration

All settings go in your Django `settings.py` with the `BOOST_` prefix.
No changes to `INSTALLED_APPS` are required.

> **Optional browser log capture** — add `django_boost` to `INSTALLED_APPS`, include
  `django_boost.urls`, and add `django_boost.middleware.InjectBoost` only if you want
  the browser console log feature.

```python
# Master switch
BOOST_ENABLED = True

# Browser console log capture
BOOST_BROWSER_LOGS_WATCHER = True
BOOST_BROWSER_LOG_LEVELS = ["error", "warning", "info", "debug"]

# Project rules (.ai/rules/)
BOOST_RULES_ENABLED = True
BOOST_RULES_SCOPED_GUIDELINES = False

# Exclude specific guidelines or skills
BOOST_GUIDELINES_EXCLUDE = []
BOOST_SKILLS_EXCLUDE = []

# Tinker tool — OFF by default for safety
BOOST_TINKER_TOOL_ENABLED = False

# Custom executable paths (auto-detected if not set)
BOOST_EXECUTABLE_PATHS = {
    "python": None,  # e.g., "/usr/bin/python3.12"
    "pip": None,
    "npm": None,
}


# MCP tool timeout (seconds)
BOOST_MCP_TOOL_TIMEOUT = 30

# Agent-specific overrides
BOOST_AGENTS = {
    "pi": {
        "guidelines_path": "AGENTS.md",
        "skills_path": ".pi/skills",
    }
}
```

---

## AI Guidelines Included

Django Boost ships with curated guidelines for the Django ecosystem:

| Template | Scope |
|----------|-------|
| `foundation.html` | General Django/Python conventions, skills activation |
| `django/core.html` | Models, views, URLs, forms, migrations, DRF |
| `python/core.html` | Type hints, imports, error handling, async, performance |
| `pytest/core.html` | pytest setup, fixtures, factories, coverage |
| `drf/core.html` | DRF serializers, viewsets, permissions, pagination |
| `htmx/core.html` | HTMX + Alpine.js patterns for Django |
| `celery/core.html` | Tasks, brokers, beat, testing, monitoring |
| `docker/core.html` | Docker Compose local development |
| `ruff/core.html` | Ruff formatting and linting |
| `deployments/core.html` | gunicorn, nginx, whitenoise, production settings |
| `django_unicorn/core.html` | Reactive components (Django's Livewire equivalent) |
| `packages.html` | **Auto-generated** — installed package versions table |
| `django_boost/core.html` | Self-referential: Boost tools and usage |

> 💡 **Key Packages** is auto-generated each time you run `boost_install` or
> `boost_update` — it scans your installed packages and writes their exact
> versions into the guidelines so AI agents always know what you're using.

Custom guidelines go in `.ai/guidelines/` and persist across updates.

---

## Project Rules

Rules are stored as markdown files in `.ai/rules/` with YAML frontmatter:

```markdown
---
paths:
  - apps/users/models.py
  - apps/users/managers.py
---

# User Model Conventions

Always extend AbstractBaseUser, not AbstractUser.
Use email as the USERNAME_FIELD.
```

Agents read applicable rules by matching the current file path against the `paths` globs in the [index](.ai/rules/index.md).

---

## Browser Logger

When enabled, Boost injects a small JS snippet into HTML responses that captures:

- `console.error`, `console.warn`, `console.info`, `console.log`, `console.table`
- `window.onerror` (uncaught exceptions)
- `unhandledrejection` (unhandled Promise rejections)

Logs are sent to `/_boost/browser-logs` and stored in `storage/logs/browser.log`, accessible to the AI agent via the `browser-logs` tool.

---

## Development

```bash
# Clone and install in development mode
git clone https://github.com/sforna/django-boost.git
cd django-boost

# With uv
uv sync
uv pip install -e ".[dev]"

# With pip
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

---

## License

MIT © Simone Fornasiere
