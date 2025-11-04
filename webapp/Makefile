UV_RUN := uv run

init-dev:
	cp .env.example .env
	uv self update
	uv python install
	make sync
	make migrate

sync:
	uv sync

migrate:
	$(UV_RUN) python manage.py migrate

run-webapp:
	$(UV_RUN) python manage.py runserver 0.0.0.0:8000

run:
	$(UV_RUN) honcho start -f Procfile.dev

run-all:
	docker-compose up -d
	sleep 5
	$(UV_RUN) honcho start -f Procfile.dev

run-docker:
	docker compose -f ../docker-compose.yml up -d

run-webapp:
	make run-docker
	sleep 5
	make run

makemessages:
	$(UV_RUN) python manage.py makemessages -l fr

compilemessages:
	$(UV_RUN) python manage.py compilemessages -l fr

check-format:
	uv run black --check --diff .
