# Brico

## Installation

Copie `.env.template` to `.env` and fill it with your own values.

```sh
cp .env.template .env
```

Install dependencies.

```sh
pip install poetry
poetry install
```

Run migrations.

```sh
python manage.py migrate
```

## Manage translations

To create a new translation file:

```sh
python manage.py makemessages -l fr
```

To compile the translations:

```sh
python manage.py compilemessages -l fr
```

Edit the translation file `locale/fr/LC_MESSAGES/django.po`

Run the project.

```sh
honcho start -f Procfile.dev
```
