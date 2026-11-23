# Claude Code — COSQUA

Ce dépôt utilise le même harnais agent que Cursor.

**Lire en priorité** : [../HARNESS.md](../HARNESS.md)

- **Délégation** : tâches simples → modèle rapide / exploration ciblée ; architecture → modèle principal. Voir `agents/skills/delegate-tasks/SKILL.md`.
- **Skills projet** : `agents/skills/` (`cosqua-webapp`, `cosqua-mobile`, `cosqua-docs`, `harness-sync`).
- **Monorepo** : [../CLAUDE.md](../CLAUDE.md) et `*/AGENTS.md`.
- **Hooks** : les hooks Cursor (`.cursor/hooks.json`) ne s’exécutent pas dans Claude Code — appliquer manuellement `harness-sync` après changements structurants.
- **Git** : **jamais** de `commit`, `push`, `add` ni autre écriture git/gh — skill `no-git-writes`, détail dans `HARNESS.md`.
