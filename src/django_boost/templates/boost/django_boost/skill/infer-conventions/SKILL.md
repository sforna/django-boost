# Infer Conventions

Infer and record coding conventions from the existing codebase.

## Purpose
This skill scans your project's code to identify recurring patterns and conventions, then records them as permanent project rules so every AI agent follows them consistently.

## When to Use
- After initial project setup to capture existing conventions.
- When onboarding new team members.
- When you notice agents making inconsistent style choices.
- Periodically as the project evolves.

## Process
1. **Scan** key directories: models, views, urls, forms, serializers, templates.
2. **Identify** patterns in naming, structure, error handling, import style, testing patterns.
3. **Record** each convention using the `record-rule` MCP tool with appropriate globs.
4. **Review** the recorded rules for accuracy.

## What to Look For

### Naming Conventions
- Model class naming (singular? PascalCase?)
- View function/class naming (snake_case? detail_view?)
- URL pattern naming (app-name:view-name?)
- Template file organization
- Test file and class naming

### Structure Patterns
- Where are views defined? (views.py per app? modules?)
- How are imports organized?
- How is error handling done?
- How is logging configured?

### Django-Specific
- CBV vs FBV preference
- Serializer style (Meta class options, field naming)
- Form layout approach
- Template inheritance patterns
- Static file organization
- Migration strategy

### Testing
- Test framework: pytest or unittest?
- Factory library: factory_boy or model_bakery?
- Test database: in-memory SQLite or test PostgreSQL?
- Coverage expectations

## Output
Record each convention as a separate rule with appropriate file globs. For example:
- `make record-rule "apps/*/models.py" "Model naming" "Models use PascalCase, singular names (User, BlogPost)"`
- `make record-rule "apps/*/views.py" "View style" "Views use class-based views with descriptive names"`

## Important
- Only record conventions that are consistently followed across the codebase.
- Don't record exceptions as conventions.
- Use specific examples from the codebase in rule notes.
- Update existing rules rather than creating duplicates.
