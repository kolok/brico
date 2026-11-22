# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**COSQUA** is a monorepo containing three applications:

- **[webapp/](./webapp/)** – Django REST backend + Hotwire frontend (Python + TypeScript)
- **[mobileapp/](./mobileapp/)** – Flutter mobile application (Dart)
- **[docs/](./docs/)** – Sphinx documentation (reStructuredText)
- **Shared infrastructure** – PostgreSQL database via `docker-compose.yml`

All code is in **English**.

---

## Quick Start

### First Time Setup

```bash
cd webapp
make init-dev              # Sets up everything: .env, Python, npm, Docker, migrations
make run-all               # Start Docker + dev servers
```

Visit `http://localhost:8000` to access the webapp.

### Subsequent Development

```bash
cd webapp
make run-all               # Starts Docker + all dev services (best approach)
# OR
make run-docker && make run  # Start Docker and dev servers separately
```

---

## Repository Structure

```
brico/
├── webapp/                 # Django + Hotwire application
│   ├── AGENTS.md          # Detailed guidance (read this for webapp work)
│   ├── core/              # Django project config
│   ├── audits/            # Domain app
│   ├── organization/       # Domain app
│   ├── static/            # Frontend assets (TS/CSS)
│   ├── templates/         # Django templates
│   ├── Makefile           # Development commands
│   └── manage.py          # Django CLI
├── mobileapp/             # Flutter application
│   ├── AGENTS.md          # Detailed guidance (read this for mobile work)
│   ├── lib/               # Dart source
│   ├── test/              # Unit & widget tests
│   └── Makefile           # Development commands
├── docs/                  # Sphinx documentation
│   ├── AGENTS.md          # Detailed guidance (read this for docs work)
│   ├── sources/           # Documentation content
│   └── Makefile           # Build commands
├── docker-compose.yml     # PostgreSQL service definition
├── CLAUDE.md              # This file (monorepo overview)
└── README.md              # Project description
```

---

## Documentation by Component

For detailed guidance on each component, refer to:

- **Webapp development**: [webapp/AGENTS.md](./webapp/AGENTS.md)
  - Complete setup, commands, architecture, testing, code standards
  - Covers Django, REST endpoints, Hotwire, TypeScript/CSS, i18n

- **Mobile app development**: [mobileapp/AGENTS.md](./mobileapp/AGENTS.md)
  - Complete setup, commands, architecture, testing, code standards
  - Covers Flutter, Dart, widgets, services, localization

- **Documentation**: [docs/AGENTS.md](./docs/AGENTS.md)
  - Structure, writing guidelines, build commands
  - How-to vs. reference documentation patterns

---

## Shared Infrastructure: PostgreSQL

All applications share a single PostgreSQL database running in Docker.

### Docker Setup

**Start services**:

```bash
cd webapp
make run-docker          # Starts PostgreSQL in Docker
# OR
docker-compose -f docker-compose.yml up -d
```

**Stop services**:

```bash
make stop-docker         # Stops PostgreSQL
# OR
docker-compose -f docker-compose.yml down
```

**View logs**:

```bash
make logs-docker         # Stream Docker logs
```

### Database Access

- **Connection**: PostgreSQL on `localhost:5432`
- **Username**: `cosqua`
- **Password**: `cosqua`
- **Database**: `cosqua`
- **Data persistence**: Volume at `pgdata/` (do not commit)

Configure in `.env`:

```bash
DATABASE_URL=postgresql://cosqua:cosqua@localhost:5432/cosqua # pragma: allowlist secret
```

---

## Common Development Tasks

### Webapp (Django + Hotwire)

```bash
cd webapp

# Setup
make init-dev              # First-time setup

# Running
make run-all               # Docker + Django + Parcel (recommended)
make run                   # Django + Parcel only (Docker must be running)

# Testing & Quality
make test                  # Run all tests
make lint                  # Lint Python
make format                # Format Python code
make npm-lint              # Lint TypeScript/CSS

# Database
make migrate               # Apply migrations
make makemigrations        # Create migrations from models

# Frontend
make npm-build             # Build TypeScript/CSS
make npm-watch             # Watch and rebuild on changes

# Translations
make makemessages          # Extract translatable strings
make compilemessages       # Compile French translations

# Cleanup
make clean                 # Remove caches and generated files
```

See [webapp/AGENTS.md](./webapp/AGENTS.md) for detailed information.

### Mobile App (Flutter)

```bash
cd mobileapp

# Setup
make install               # Install Flutter dependencies

# Running
make run                   # Launch app on device/emulator
make hot-reload            # Run with hot reload

# Testing & Quality
make test                  # Run all tests
make analyze               # Lint code
make format                # Format code
make lint                  # Analyze + format

# Localization
make localizations         # Generate l10n code after editing ARB files

# Building
make build-android-apk     # Build APK
make build-android-aab     # Build AAB (Play Store)
make build-ios             # Build iOS
make build-web             # Build web

# Cleanup
make clean                 # Clean build artifacts
```

See [mobileapp/AGENTS.md](./mobileapp/AGENTS.md) for detailed information.

### Documentation

```bash
cd docs

# Build
make build-docs            # Build HTML documentation
```

Output: `_build/html/` (do not commit)

See [docs/AGENTS.md](./docs/AGENTS.md) for detailed information.

---

## Development Workflow

### Before Making Changes

1. **Check which component** you're working on (webapp, mobile, or docs)
2. **Read the relevant AGENTS.md** for that component (detailed guidance, patterns, standards)
3. **Understand the architecture** by exploring the component's code structure

### Making Changes

1. **Explore**: Find the minimal set of files to understand current behavior
2. **Plan**: Identify the smallest change that satisfies the request
3. **Implement**: Write code following the component's standards
4. **Test**: Run tests for the touched area
5. **Quality**: Run linting, formatting, and analysis tools
6. **Verify**: Ensure all tests pass and no new issues introduced

### Before Committing

1. Run tests: `make test` (or equivalent for your component)
2. Run linting/formatting: `make lint && make format` (or equivalent)
3. Review changes for quality and correctness
4. Write a concise, descriptive commit message
5. Push to the repository

---

## Repository Hygiene Rules

### Never Commit

- `.env` – local environment secrets
- `static/compiled/` – generated Parcel output (webapp)
- `__pycache__/`, `*.pyc` – Python cache
- `.pytest_cache/`, `.parcel-cache/` – build caches
- `pgdata/` – local database data
- `_build/` – generated documentation
- Flutter generated files in `lib/generated/`
- Build artifacts (`.apk`, `.ipa`, `.aab`)

### Keep Committed

- `Makefile`, source code, tests
- Django migrations (`*/migrations/*.py`)
- Translation files (`*.po`, `*.mo` for Django; `*.arb` for Flutter)
- `package-lock.json`, `pubspec.lock` – dependency locks

---

## Technology Stack

| Component  | Backend          | Frontend                                  | Database   | Build         |
| ---------- | ---------------- | ----------------------------------------- | ---------- | ------------- |
| **Webapp** | Django 4.x + DRF | Hotwire (Turbo/Stimulus), TypeScript, CSS | PostgreSQL | Parcel, uv    |
| **Mobile** | —                | Flutter/Dart                              | —          | Flutter build |
| **Docs**   | —                | reStructuredText                          | —          | Sphinx        |

### Language Requirements

- **Python**: 3.13+ (managed by `uv`)
- **Node.js**: Latest LTS (for npm)
- **Dart/Flutter**: Latest stable
- **All code**: English

---

## Code Standards Summary

### Python (Webapp Backend)

- PEP 8 via Black formatter
- Ruff linting
- Type hints required
- Docstrings for public functions

### TypeScript/CSS (Webapp Frontend)

- ESLint + Prettier
- camelCase naming
- No React/Vue – use Hotwire instead

### Dart (Mobile App)

- Official Dart conventions
- Immutable widgets preferred
- Line length: 120 characters
- Type annotations required

---

## Troubleshooting Quick Links

### Webapp Issues

- Database won't connect → Check Docker running, `.env` DATABASE_URL
- Tests fail → Ensure `make migrate` run, check for conflicting test data
- Frontend doesn't update → Run `make npm-watch` to rebuild
- See [webapp/AGENTS.md#Troubleshooting](./webapp/AGENTS.md#troubleshooting) for more

### Mobile Issues

- Build fails → Run `make clean`, ensure dependencies updated
- Tests fail → Check analyzer output, run `make localizations` if ARB changed
- Localization missing → Run `make localizations` after editing ARB files
- See [mobileapp/AGENTS.md#Troubleshooting](./mobileapp/AGENTS.md#troubleshooting) for more

---

## Getting Help

For **detailed guidance** on any component:

- **Webapp**: See [webapp/AGENTS.md](./webapp/AGENTS.md), [webapp/templates.AGENTS.md](./webapp/templates.AGENTS.md), [webapp/env.AGENTS.md](./webapp/env.AGENTS.md)
- **Mobile**: See [mobileapp/AGENTS.md](./mobileapp/AGENTS.md)
- **Docs**: See [docs/AGENTS.md](./docs/AGENTS.md)

For **general help** with Claude Code: `/help`

For **bugs or feedback**: https://github.com/anthropics/claude-code/issues
