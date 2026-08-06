# Piano di Conversione: laravel-boost → django-boost

## 📐 Architettura di laravel-boost (cosa stiamo convertendo)

```
laravel-boost/
├── .ai/                    # 43 template Blade per guidelines/skills
├── src/
│   ├── Mcp/                # Server MCP, 11 tool, 4 prompt, driver schema
│   ├── Install/            # Agenti (13), Writer, Composer, Detection
│   ├── Console/            # 6 comandi Artisan
│   ├── Rules/              # Gestione project rules (.ai/rules/)
│   ├── Skills/Remote/      # Download skill da GitHub + audit
│   ├── Concerns/           # 3 trait PHP
│   ├── Services/           # BrowserLogger
│   ├── Middleware/          # InjectBoost
│   ├── Support/            # Config, Composer, Npm, etc.
│   └── Contracts/          # 3 interfacce
├── config/boost.php        # Configurazione
└── tests/                  # ~200 test
```

---

## 🗺️ Piano modulare (5 fasi, ~18 moduli)

### FASE 1 — Scheletro e Core ⚙️

| # | Modulo | File | Note Django |
|---|--------|------|-------------|
| 1.1 | `pyproject.toml` | package metadata, `django_boost` | equivalente a `composer.json` |
| 1.2 | `DjangoBoostConfig` | `apps.py` | `AppConfig` con `ready()` per registrare segnali/MCP |
| 1.3 | `config.py` / `settings.py` | `boost_settings.py` | settings Django-based, `BOOST_ENABLED`, `BOOST_BROWSER_LOGS_WATCHER` etc. |
| 1.4 | `urls.py` | route `_boost/browser-logs` | equivalente alla route POST in `BoostServiceProvider` |
| 1.5 | `middleware.py` | `InjectBoost` | inietta script JS nel HTML (come `@boostJs`) |
| 1.6 | Struttura directory | `src/django_boost/` | `mcp/`, `install/`, `management/`, `skills/`, `rules/`, `services/`, `templates/` |

**Tempo stimato**: 1-2 giorni

---

### FASE 2 — MCP Server (cuore del progetto) 🔌

Il server MCP va implementato con il **Python SDK ufficiale `mcp`** (o `fastmcp`).

| # | Tool MCP | Tipo | Complessità | Note |
|---|----------|------|-------------|------|
| 2.1 | **ApplicationInfo** | ReadOnly | Bassa | Django version, Python version, packages (da `pip freeze`) |
| 2.2 | **DatabaseConnections** | ReadOnly | Bassa | `settings.DATABASES` keys |
| 2.3 | **DatabaseSchema** | ReadOnly | **Media** | `connection.introspection.table_names()`, `get_table_description()`. Driver per PostgreSQL, MySQL, SQLite |
| 2.4 | **DatabaseQuery** | ReadOnly | **Alta** | Read-only SQL parser con stesso algoritmo di sicurezza (CTE, EXPLAIN, INTO detection). Django raw queries |
| 2.5 | **LastError** | ReadOnly | Bassa | Log file parsing + cache |
| 2.6 | **ReadLogEntries** | ReadOnly | Bassa | `tail + grep` file di log Django |
| 2.7 | **BrowserLogs** | ReadOnly | Bassa | Legge `storage/logs/browser.log` |
| 2.8 | **GetAbsoluteUrl** | ReadOnly | Bassa | `django.urls.reverse` + `request.build_absolute_uri` |
| 2.9 | **SearchDocs** | ReadOnly | Media | Richiede API equivalente a `boost.laravel.com` o scraping docs.djangoproject.com |
| 2.10 | **RecordRule** | Scrittura | Media | Scrive file `.ai/rules/*.md` con frontmatter YAML |
| 2.11 | **Tinker** | Tool | Bassa | Shell Django (`manage.py shell -c`) |
| 2.12 | **Server MCP** | - | entry point | `manage.py boost:mcp` (equivalente a `Boost::class` + `CallToolWithExecutor`) |

**Dipendenze**: Fase 1 completata
**Tempo stimato**: 4-6 giorni

---

### FASE 3 — CLI e Install System 🖥️

#### Comandi Django Management

| # | Comando | Descrizione |
|---|---------|-------------|
| 3.1 | `boost_install` | Equivalente a `boost:install` con `rich` per la TUI |
| 3.2 | `boost_update` | Aggiorna guidelines/skills esistenti |
| 3.3 | `boost_add_skill` | Scarica skill da GitHub |
| 3.4 | `boost_list_skill` | Elenca skill disponibili |
| 3.5 | `boost_mcp` | Avvia server MCP |
| 3.6 | `boost_execute_tool` | Esecuzione command-line di un tool |

#### Install System

| # | Modulo | Descrizione |
|---|--------|-------------|
| 3.7 | `install/agents/` | Agenti Python: `Agent` base, `Pi`, `Cursor`, `Copilot`, `Codex`, `ClaudeCode`, `Zed`, `Amp`, `OpenCode`, `GrokBuild` |
| 3.8 | `install/agents_detector.py` | Detect agenti installati su sistema e progetto |
| 3.9 | `install/guideline_writer.py` | Scrive `<django-boost-guidelines>` nei file agente |
| 3.10 | `install/skill_writer.py` | Sync skill directories |
| 3.11 | `install/mcp_writer.py` | Scrive config MCP nei file agente |
| 3.12 | `install/guideline_composer.py` | Scopre e renderizza template Jinja2 |
| 3.13 | `install/skill_composer.py` | Scopre skills (core, built-in, third-party, user) |
| 3.14 | `install/rule_composer.py` | Estrae path-scoped guidelines |

**Dipendenze**: Fase 2 completata
**Tempo stimato**: 5-7 giorni

---

### FASE 4 — Templates e Guidelines (`.ai/`) 📝

Conversione dei 43 template Blade in template Jinja2 per l'ecosistema Django.

| Categoria Laravel | Equivalente Django |
|---|---|
| `foundation.blade.php` | Linee guida generali Django/Python |
| `laravel/core.blade.php` | `django/core.html` (convenzioni Django, `manage.py` commands) |
| `pest/core.blade.php` + skill | `pytest/core.html` + `pytest/skill/` |
| `phpunit/core.blade.php` | `unittest/core.html` |
| `php/core.blade.php` + versioni | `python/core.html` + versioni (3.10, 3.11, 3.12, 3.13) |
| `livewire/core.blade.php` + skill | `htmx/core.html` + skill (HTMX + Alpine.js) |
| `inertia-vue/core.blade.php` | `inertia-django/core.html` (se si usa django-inertia) |
| `inertia-react/` | idem per React |
| `inertia-svelte/` | idem per Svelte |
| `fluxui-free/` + `fluxui-pro/` | `daisyui/` o `flowbite/` |
| `folio/` | N/A (routing filesystem Laravel-only) |
| `volt/` | `django-unicorn/` |
| `sail/core.blade.php` | `docker/core.html` (Docker Compose development) |
| `pint/core.blade.php` | `ruff/core.html` o `black/core.html` |
| `mcp/skill/` | Skill generica MCP (riutilizzabile) |
| `wayfinder/` | N/A (IDE Laravel) |
| `deployments/core.blade.php` | `deployments/core.html` (gunicorn, whitenoise, etc.) |
| `herd/core.blade.php` | N/A (Herd è macOS-only Laravel) |
| `enforce-tests.blade.php` | `enforce-tests.html` |
| `boost/` | `django_boost/` guidelines auto-referenziali |

**Rendering engine**: Jinja2 con sistema di placeholder per backtick (come `RendersBladeGuidelines`)

**Dipendenze**: Fase 3 completata
**Tempo stimato**: 5-8 giorni

---

### FASE 5 — Servizi e rifiniture ✨

| # | Modulo | Descrizione |
|---|--------|-------------|
| 5.1 | `services/browser_logger.py` | Template tag Django `{% boost_js %}` + script JS |
| 5.2 | `rules/rule_repository.py` | Gestione `.ai/rules/` (frontmatter YAML, sync, index) |
| 5.3 | `skills/remote/` | `GitHubSkillProvider`, `RemoteSkill`, `SkillAuditor` |
| 5.4 | `skills/remote/github_repository.py` | Classe per interagire con repo GitHub |
| 5.5 | `support/package_registry.py` | Mappa nomi pacchetti `pip` → nomi "roster" |
| 5.6 | `support/render_failures.py` | Tracciamento fallimenti rendering |
| 5.7 | `support/command_normalizer.py` | Normalizza comandi shell (cross-platform) |
| 5.8 | `tests/` | Test suite con pytest |

**Tempo stimato**: 4-6 giorni

---

## 📊 Riepilogo

| Fase | Contenuto | Tempo stimato |
|------|-----------|---------------|
| 1 | Scheletro + Core | 1-2 giorni |
| 2 | MCP Server (11 tool) | 4-6 giorni |
| 3 | CLI + Install System (13 agenti) | 5-7 giorni |
| 4 | Templates .ai (~25 template Django) | 5-8 giorni |
| 5 | Servizi, Rules, Skills Remote, Test | 4-6 giorni |
| **Totale** | | **19-29 giorni** |

---

## 🔑 Decisioni architetturali chiave

1. **MCP SDK**: `fastmcp` (API più semplice dell'SDK `mcp` ufficiale)
2. **Rendering template**: Jinja2 (più flessibile e disaccoppiato da Django)
3. **TUI**: `rich` + `questionary` (equivalente Python di `laravel/prompts`)
4. **Package name**: `django-boost` su PyPI
5. **Agenti**: configurazioni in file JSON/Markdown/TOML — **riutilizzabili quasi immutate** da laravel-boost, vanno solo rigenerate da Python

---

## 📁 Struttura directory target

```
django-boost/
├── pyproject.toml
├── README.md
├── LICENSE.md
├── src/
│   └── django_boost/
│       ├── __init__.py
│       ├── apps.py                  # DjangoBoostConfig
│       ├── config.py                # boost_settings
│       ├── urls.py                  # /_boost/browser-logs
│       ├── middleware.py            # InjectBoost
│       ├── mcp/
│       │   ├── __init__.py
│       │   ├── server.py            # DjangoBoost MCPServer
│       │   ├── tool_executor.py
│       │   ├── tool_registry.py
│       │   ├── tools/
│       │   │   ├── application_info.py
│       │   │   ├── browser_logs.py
│       │   │   ├── database_connections.py
│       │   │   ├── database_query.py
│       │   │   ├── database_schema/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── base.py
│       │   │   │   ├── sqlite.py
│       │   │   │   ├── mysql.py
│       │   │   │   ├── postgresql.py
│       │   │   │   └── null.py
│       │   │   ├── get_absolute_url.py
│       │   │   ├── last_error.py
│       │   │   ├── read_log_entries.py
│       │   │   ├── record_rule.py
│       │   │   ├── search_docs.py
│       │   │   └── tinker.py
│       │   ├── prompts/
│       │   └── resources/
│       ├── install/
│       │   ├── agents/
│       │   │   ├── __init__.py
│       │   │   ├── agent.py
│       │   │   ├── pi.py
│       │   │   ├── cursor.py
│       │   │   ├── copilot.py
│       │   │   ├── codex.py
│       │   │   ├── claude_code.py
│       │   │   ├── zed.py
│       │   │   ├── amp.py
│       │   │   ├── opencode.py
│       │   │   └── grok_build.py
│       │   ├── agents_detector.py
│       │   ├── guideline_writer.py
│       │   ├── skill_writer.py
│       │   ├── mcp_writer.py
│       │   ├── guideline_composer.py
│       │   ├── skill_composer.py
│       │   ├── rule_composer.py
│       │   ├── detection/
│       │   └── enums/
│       ├── management/
│       │   └── commands/
│       │       ├── boost_install.py
│       │       ├── boost_update.py
│       │       ├── boost_add_skill.py
│       │       ├── boost_list_skill.py
│       │       ├── boost_mcp.py
│       │       └── boost_execute_tool.py
│       ├── rules/
│       │   ├── __init__.py
│       │   ├── rule_repository.py
│       │   └── rule_frontmatter.py
│       ├── skills/
│       │   └── remote/
│       │       ├── __init__.py
│       │       ├── github_skill_provider.py
│       │       ├── github_repository.py
│       │       ├── remote_skill.py
│       │       └── skill_auditor.py
│       ├── services/
│       │   └── browser_logger.py
│       ├── support/
│       │   ├── package_registry.py
│       │   ├── render_failures.py
│       │   └── command_normalizer.py
│       └── templates/
│           └── boost/             # .ai/ templates Django
│               ├── foundation.html
│               ├── django/
│               ├── pytest/
│               ├── htmx/
│               ├── docker/
│               └── ...
└── tests/
    ├── test_mcp_tools/
    ├── test_install/
    └── test_management/
```
