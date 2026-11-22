---
name: cosqua-mobile
description: Runs Flutter development workflows for COSQUA mobileapp. Use when editing mobileapp/, Dart widgets, pubspec, or mobile Make targets.
---

# COSQUA Mobile

## Avant de coder

1. Lire [mobileapp/AGENTS.md](../../../mobileapp/AGENTS.md).
2. Explorations de structure : sous-agent `explore` ou modèle rapide — voir [delegate-tasks](../delegate-tasks/SKILL.md).

## Commandes (depuis `mobileapp/`)

| Action          | Commande                                   |
| --------------- | ------------------------------------------ |
| Dépendances     | `make install`                             |
| Run             | `make run`                                 |
| Tests / qualité | `make test`, `make analyze`, `make format` |
| l10n            | `make localizations` après édition des ARB |

## Règles clés

- Conventions Dart officielles, widgets immutables si possible.
- Ligne 120 caractères max.
- Code en **anglais**.

## Après modification

- `Makefile` ou `pubspec.yaml` → [harness-sync](../harness-sync/SKILL.md).
