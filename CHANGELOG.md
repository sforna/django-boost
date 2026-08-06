# Changelog

All notable changes to Django Boost will be documented in this file.

## [0.1.0](https://github.com/sforna/django-boost/releases/tag/v0.1.0) - unreleased

- Initial release of Django Boost
- 11 MCP tools: ApplicationInfo, BrowserLogs, DatabaseConnections, DatabaseQuery, DatabaseSchema, GetAbsoluteUrl, LastError, ReadLogEntries, RecordRule, SearchDocs, Tinker
- 9 AI agent integrations: Pi, Cursor, Copilot, Codex, Claude Code, Zed, Amp, OpenCode, Grok Build
- 14 curated AI guidelines for Django ecosystem (Django, pytest, DRF, HTMX, Celery, Docker, Ruff, etc.)
- 6 management commands: boost:install, boost:update, boost:mcp, boost:add-skill, boost:list-skill, boost:execute-tool
- Browser logger middleware for JS console error capture
- Project rules system (.ai/rules/) with YAML frontmatter
- GitHub-based skill discovery and download
- SQL read-only validator (ported from laravel-boost)
- Database schema drivers for SQLite, PostgreSQL, MySQL
- 83 tests passing
