---
name: cosqua-docs
description: Builds and edits Sphinx documentation for COSQUA. Use when editing docs/, reStructuredText, or docs Makefile.
---

# COSQUA Documentation

## Avant de coder

1. Lire [docs/AGENTS.md](../../../docs/AGENTS.md).

## Commandes (depuis `docs/`)

| Action     | Commande          |
| ---------- | ----------------- |
| Build HTML | `make build-docs` |

Sortie : `_build/html/` (ne pas committer).

## Règles

- Contenu documentation : conventions du repo (souvent anglais pour le code ; suivre `docs/AGENTS.md` pour la langue des pages).
- How-to vs référence : patterns décrits dans `docs/AGENTS.md`.

## Après modification

- `Makefile` ou `conf.py` → [harness-sync](../harness-sync/SKILL.md).
