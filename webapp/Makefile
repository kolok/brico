# Variables
UV_RUN := uv run
DOCKER_COMPOSE := docker compose
DOCKER_COMPOSE_FILE := ../docker-compose.yml
MANAGE_PY := $(UV_RUN) python manage.py

.PHONY: help init-dev sync migrate run-server run run-all run-webapp run-docker stop logs \
        makemessages compilemessages check-format format lint test clean shell \
        npm-install npm-build npm-watch npm-lint

# Cible par défaut
help:
	@echo "Commandes disponibles:"
	@echo "  make init-dev          - Initialiser l'environnement de développement"
	@echo "  make run-webapp        - Démarrer l'application complète (Docker + webapp)"
	@echo "  make run               - Démarrer l'application avec honcho"
	@echo "  make run-server        - Démarrer uniquement le serveur Django"
	@echo "  make run-docker        - Démarrer uniquement les services Docker"
	@echo "  make stop              - Arrêter les conteneurs Docker"
	@echo "  make test              - Exécuter les tests"
	@echo "  make format            - Formater le code"
	@echo "  make lint              - Vérifier le code"
	@echo "  make clean             - Nettoyer les fichiers temporaires"

# Initialisation
init-dev:
	cp .env.example .env
	uv self update
	uv python install
	make sync
	make migrate

sync:
	uv sync

# Base de données
migrate:
	$(MANAGE_PY) migrate

# Exécution
run-server:
	$(MANAGE_PY) runserver 0.0.0.0:8000

run:
	$(UV_RUN) honcho start -f Procfile.dev

run-docker:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d

run-webapp: run-docker
	@echo "Attente du démarrage de Docker..."
	@sleep 5
	make run

run-all: run-docker
	@echo "Attente du démarrage de Docker..."
	@sleep 5
	$(UV_RUN) honcho start -f Procfile.dev

stop:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down

logs:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f

# Internationalisation
makemessages:
	$(MANAGE_PY) makemessages -l fr

compilemessages:
	$(MANAGE_PY) compilemessages -l fr

# Qualité du code Python
check-format:
	$(UV_RUN) black --check --diff .

format:
	$(UV_RUN) black .

lint:
	$(UV_RUN) ruff check .

# Tests
test:
	$(MANAGE_PY) test

# Outils npm
npm-install:
	npm install

npm-build:
	npm run build

npm-watch:
	npm run watch

npm-lint:
	npm run lint

# Utilitaires
shell:
	$(MANAGE_PY) shell

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .parcel-cache
	rm -rf static/compiled

# Commande complète pour tout nettoyer et redémarrer
reset: clean stop
	rm -rf pgdata
	make init-dev
	make run-webapp
