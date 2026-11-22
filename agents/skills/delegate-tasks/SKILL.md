---
name: delegate-tasks
description: Routes agent work to lighter models or specialized subagents for simple, bounded tasks. Use when planning work, before large exploration, or when the user asks about model choice. Applies to Cursor and Claude Code on COSQUA.
---

# Délégation des tâches (COSQUA)

## Principe

Les **tâches simples** sont déléguées à des **modèles moins puissants mais suffisants**, ou à des **sous-agents spécialisés**, pour préserver le modèle principal pour l’architecture et les changements à risque.

## Décision rapide

```
La tâche est-elle mécanique et vérifiable (lint, format, un test, grep, find file) ?
  → OUI : modèle rapide / shell direct / explore quick
  → NON : continuer

La tâche est-elle une exploration large sans écriture ?
  → OUI : subagent explore (quick ou medium)
  → NON : continuer

La tâche touche-t-elle auth, migrations, perf, API publique, multi-app ?
  → OUI : modèle principal + AGENTS.md du composant
```

## Cursor

| Besoin                  | Action                                              |
| ----------------------- | --------------------------------------------------- |
| Trouver du code         | `Task` + `explore`, thoroughness `quick`            |
| PR CI                   | `Task` + `ci-investigator`                          |
| Revue sécurité demandée | skill `review-security` ou subagent dédié           |
| Fix one-liner + tests   | Shell `make test` / `pytest` ciblé, pas de refactor |

Choisir un modèle **fast** lorsque l’UI propose plusieurs modèles pour un sous-agent.

## Claude Code

- Limiter les lectures : chercher puis lire 3–5 fichiers pertinents.
- Ne pas réécrire le monorepo dans un seul message ; plan court puis edits.
- Même tableau de décision que ci-dessus.

## Exemples

**Déléguer** : « Où est défini `ProjectAuditView` ? », `make format`, « lance pytest sur test_prompt.py ».

**Ne pas déléguer** : nouveau flux d’autorisation, refactor modèles + migrations, changement Turbo/Stimulus transversal.
