# Variables
UV_RUN := uv run
DOCKER_COMPOSE := docker compose
DOCKER_COMPOSE_FILE := ../docker-compose.yml
MANAGE_PY := $(UV_RUN) python manage.py
PYTEST := $(UV_RUN) pytest

# Cible par défaut
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make init-dev          - Initialize the development environment"
	@echo "  make sync              - Sync Python dependencies with uv"
	@echo "  make migrate           - Run Django database migrations"
	@echo "  make run-webapp        - Start the complete application (Docker + webapp)"
	@echo "  make run               - Start the application with honcho"
	@echo "  make run-all           - Start Docker services and run honcho"
	@echo "  make runserver         - Start only the Django server"
	@echo "  make run-docker        - Start only Docker services"
	@echo "  make stop-docker       - Stop Docker containers"
	@echo "  make logs-docker       - Show Docker logs"
	@echo "  make test              - Run tests"
	@echo "  make format            - Format the code"
	@echo "  make check-format      - Check code formatting"
	@echo "  make lint              - Lint the code"
	@echo "  make npm-install       - Install npm dependencies"
	@echo "  make npm-build         - Build frontend assets"
	@echo "  make npm-watch         - Watch and rebuild frontend assets"
	@echo "  make npm-lint          - Lint frontend code"
	@echo "  make shell             - Open Django shell"
	@echo "  make makemessages      - Extract translation messages"
	@echo "  make compilemessages   - Compile translation messages"
	@echo "  make clean             - Clean temporary files"
	@echo "  make reset             - Reset everything (clean + stop-docker + reinit)"

.PHONY: init-dev
init-dev:
	cp .env.template .env
	uv self update
	uv python install
	make run-docker
	sleep 5
	make sync
	make migrate
	make npm-install

.PHONY: sync
sync:
	uv sync

.PHONY: run
run:
	$(UV_RUN) honcho start -f Procfile.dev

.PHONY: run-docker
run-docker:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d

.PHONY: run-webapp
run-webapp: run-docker
	@echo "Attente du démarrage de Docker..."
	@sleep 5
	make run

.PHONY: run-all
run-all: run-docker
	@echo "Attente du démarrage de Docker..."
	@sleep 5
	$(UV_RUN) honcho start -f Procfile.dev

.PHONY: stop-docker
stop-docker:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down

.PHONY: logs-docker
logs-docker:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f

.PHONY: runserver
run-server:
	$(MANAGE_PY) runserver

.PHONY: makemessages
makemessages:
	$(MANAGE_PY) makemessages -l fr

.PHONY: compilemessages
compilemessages:
	$(MANAGE_PY) compilemessages -l fr

.PHONY: makemigrations
makemigrations:
	$(MANAGE_PY) makemigrations

.PHONY: migrate
migrate:
	$(MANAGE_PY) migrate

.PHONY: check-format
check-format:
	$(UV_RUN) black --check --diff .

.PHONY: format
format:
	$(UV_RUN) black .

.PHONY: lint
lint:
	$(UV_RUN) ruff check .

.PHONY: test
test:
	$(PYTEST)

.PHONY: npm-install
npm-install:
	npm install

.PHONY: npm-build
npm-build:
	npm run build

.PHONY: npm-watch
npm-watch:
	npm run watch

.PHONY: npm-lint
npm-lint:
	npm run lint

.PHONY: shell
shell:
	$(MANAGE_PY) shell

.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .parcel-cache
	rm -rf .pytest_cache
	rm -rf static/compiled
	rm -rf staticfiles

.PHONY: reset
reset: clean stop-docker
	rm -rf pgdata
	make init-dev
	make run-all
