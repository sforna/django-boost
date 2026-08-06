# Contributing Guide

Thank you for considering contributing to Django Boost!

## How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feat/my-feature`)
3. **Write** your changes with tests
4. **Run** the test suite (`pytest tests/ -v`)
5. **Run** linting (`ruff check src/ tests/ && ruff format --check src/ tests/`)
6. **Submit** a pull request

## Pull Request Guidelines

- Include tests for new features or bug fixes.
- Follow existing code conventions (check sibling files).
- Keep PRs focused — one feature or fix per PR.
- Write descriptive commit messages.

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for formatting and linting:

```bash
ruff format .
ruff check --fix .
```
