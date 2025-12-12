# Webapp Agent Notes (Django + Hotwire)

## Scope

This file applies to **`webapp/` only**.

## High-level map

- **Backend (Django/DRF)**
  - Django project: `core/`
  - Domain app: `audits/` (views, models, templates, tests)
  - Domain app: `organization/`
- **Frontend (Hotwire + Parcel)**
  - Source assets: `static/to_compile/` (TS/CSS)
  - Entry points: `static/to_compile/entrypoints/main.ts`, `main.css`
  - Parcel output (**do not commit**): `static/compiled/`
  - Templates: `templates/`

## Specific Agent Notes

- **Tests** : `./env.AGENTS.md`
- **Templates** : `./templates.AGENTS.md`

## Default workflow (follow this)

1. **Explore**: search + read the minimal set of files (views/templates/tests) to understand the current behavior.
2. **Plan**: state the smallest change that satisfies the request; prefer incremental diffs.
3. **Implement**:
   - Keep changes local to the relevant app (`audits/`, `organization/`, `core/`).
   - Prefer server-rendered + Turbo/Stimulus; **do not introduce React/Vue**.
4. **Verify**:
   - Run unit tests for the touched area.
   - Run lint/format if you changed Python.
   - If you changed TS/CSS, run the frontend lint/build.

## Code Standards

- Python: PEP 8, type hints required, docstrings for public functions.
- TypeScript: ESLint + Prettier, camelCase naming.
- Language: the application and documentation are all in English

## Commands (use Make targets first)

- **Setup**: `make init-dev` (creates `.env`, installs Python + npm deps, migrates, starts Docker)
- **Install/update Python deps**: `make sync`
- **Migrations**: `make makemigrations` then `make migrate`
- **Run**:
  - Full dev (Docker + honcho): `make run-all`
  - Only honcho: `make run`
  - Only Docker: `make run-docker`
- **Tests**: `make test`
- **Specific Tests**: `uv run pytest`
- **Specific Python command**: `uv run python`
- **Specific Django command**: `uv run python manage.py`
- **Lint/format (Python)**:
  - Format: `make format` (black)
  - Lint: `make lint` (ruff)
  - Check formatting: `make check-format`
- **Frontend**:
  - Install: `make npm-install`
  - Build: `make npm-build`
  - Watch: `make npm-watch`
  - Lint: `make npm-lint`

## Quality & conventions

- **Python**: type hints required; docstrings for public functions.
- **Tests**: use pytest; add/adjust tests for bug fixes & new features.
- **Coverage**: keep backend coverage ≥ 80%.
- **i18n**:
  - Extract: `make makemessages`
  - Compile: `make compilemessages`
  - Update `locale/fr/LC_MESSAGES/django.po` and recompile.

## Templating & UI rules

- Prefer **Django templates + Turbo Frames** over custom JS.
- Keep templates small and componentized via `templates/.../components/` when appropriate.
- If adding user-facing strings, make them translatable.

## Safety / repo hygiene

- **Never commit** generated assets: `static/compiled/`.
- **Never commit secrets**: `.env` must stay local.
- Avoid broad refactors unless requested; keep diffs surgical.
