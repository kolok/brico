# Brico

## Prerequis

- installation de [UV](https://docs.astral.sh/uv/getting-started/installation/)

## Installation

Si première utilisation :

```sh
make init-dev
make run
```

Copie `.env.template` to `.env` and fill it with your own values.

```sh
cp .env.template .env
```

Install dependencies.

```sh
make sync
```

Run migrations.

```sh
make migrate
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
make run
```
