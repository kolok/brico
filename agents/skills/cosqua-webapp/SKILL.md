---
name: cosqua-webapp
description: Runs Django + Hotwire development workflows for COSQUA webapp. Use when editing webapp/, Django models, templates, Stimulus, pytest, or Make targets under webapp/.
---

# COSQUA Webapp

## Avant de coder

1. Lire [webapp/AGENTS.md](../../../webapp/AGENTS.md) (obligatoire pour tâches non triviales).
2. Sous-docs : `webapp/agents-docs/*.AGENTS.md` selon le sujet (auth, templates, tests).
3. Tâches simples (grep, un test, format) : déléguer — voir [delegate-tasks](../delegate-tasks/SKILL.md).

## Commandes (depuis `webapp/`)

| Action         | Commande                                 |
| -------------- | ---------------------------------------- |
| Dev complet    | `make run-all`                           |
| Tests          | `make test` ou `uv run pytest <path> -v` |
| Python qualité | `make format && make lint`               |
| Frontend       | `make npm-build` / `make npm-lint`       |
| Migrations     | `make makemigrations && make migrate`    |

## Règles clés

- Pas de React/Vue — Turbo + Stimulus.
- Apps domaine : `audits/`, `organization/` — changements chirurgicaux.
- Code et commentaires en **anglais**.
- Ne pas committer `static/compiled/`, `.env`.

## Après modification

- Fichiers structurants (`Makefile`, `settings.py`, `pyproject.toml`) → skill [harness-sync](../harness-sync/SKILL.md).
