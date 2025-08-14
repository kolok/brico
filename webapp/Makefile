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

makemessages:
	$(UV_RUN) python manage.py makemessages -l fr

compilemessages:
	$(UV_RUN) python manage.py compilemessages -l fr
	