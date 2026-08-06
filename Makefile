.PHONY: help install dev test lint format check clean build release

# ── Default target ────────────────────────────────────────────────
.DEFAULT_GOAL := help

# ── Variables ─────────────────────────────────────────────────────
PYTHON    := python
PIP       := pip
UV        := uv
RUFF      := ruff
MYPY      := mypy
PYTEST    := pytest
BANDIT    := bandit
SRC       := src tests

# ── Help ──────────────────────────────────────────────────────────
help: ## Mostra questo aiuto
	@echo "Django Boost — Makefile"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# ── Installation ──────────────────────────────────────────────────
install: ## Installa django-boost in development mode (pip)
	$(PIP) install -e ".[dev]"

install-uv: ## Installa django-boost in development mode (uv)
	$(UV) sync
	$(UV) pip install -e ".[dev]"

# ── Testing ───────────────────────────────────────────────────────
test: ## Esegui la test suite completa
	$(PYTEST) tests/ -v --tb=short

test-cov: ## Esegui i test con coverage report
	$(PYTEST) tests/ -v --tb=short --cov=src/django_boost --cov-report=term-missing --cov-report=html

test-db: ## Esegui i test con database (non in-memory)
	$(PYTEST) tests/ -v --tb=short --reuse-db

test-fast: ## Esegui i test in parallelo
	$(PYTEST) tests/ -v --tb=short -n auto

test-watch: ## Esegui i test ad ogni modifica file
	ptw tests/ src/ -- --tb=short

test-matrix: ## Esegui i test su più versioni Python/Django (richiede tox)
	tox run -e py310-django50,py311-django50,py312-django51,py313-django51

test-all: test lint format-check ## Esegui test + lint + format (locale)
	@echo "Tutti i check locali passati."

# ── Linting & Formatting ──────────────────────────────────────────
lint: ## Esegui linting con ruff
	$(RUFF) check $(SRC)

lint-fix: ## Esegui linting e auto-correggi
	$(RUFF) check --fix $(SRC)

format: ## Formatta il codice con ruff
	$(RUFF) format $(SRC)

format-check: ## Verifica formattazione senza modificare
	$(RUFF) format --check $(SRC)

# ── Type Checking ─────────────────────────────────────────────────
types: ## Esegui type checking con mypy
	$(MYPY) src/ --ignore-missing-imports --show-error-codes

types-strict: ## Esegui type checking rigoroso
	$(MYPY) src/ --strict --show-error-codes

# ── Security ──────────────────────────────────────────────────────
bandit: ## Analisi di sicurezza con bandit
	$(BANDIT) -r src/ -ll

bandit-full: ## Analisi di sicurezza completa (tutti i livelli)
	$(BANDIT) -r src/ -lll -v

# ── Combined checks ───────────────────────────────────────────────
check: lint format-check types test ## Esegui tutti i controlli (lint + format + types + test)

check-fast: lint format-check test ## Esegui lint + format + test (senza mypy)

ci: lint format-check types test bandit ## Esegui tutti i controlli CI

# ── Cleaning ──────────────────────────────────────────────────────
clean: ## Pulizia file generati
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete

clean-all: clean ## Pulizia completa
	rm -rf .venv/ venv/

# ── Build & Release ───────────────────────────────────────────────
build: clean ## Compila il pacchetto wheel e sdist
	$(PYTHON) -m build

publish-test: build ## Pubblica su PyPI di test
	$(PYTHON) -m twine upload --repository testpypi dist/*

publish: build ## Pubblica su PyPI
	$(PYTHON) -m twine upload dist/*

# ── Development helpers ───────────────────────────────────────────
shell: ## Apri una shell Django
	$(PYTHON) manage.py shell

serve: ## Avvia il server di sviluppo Django
	$(PYTHON) manage.py runserver

deps: ## Mostra le dipendenze installate
	$(PIP) list --format=columns | head -40

deps-outdated: ## Mostra dipendenze obsolete
	$(PIP) list --outdated
