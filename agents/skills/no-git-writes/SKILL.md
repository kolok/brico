---
name: no-git-writes
description: Forbids agent git and gh write commands on COSQUA (no commit, push, add, rebase). Use before running shell with git or gh, or when preparing to version changes.
---

# Git — lecture seule

## Règle

**Ne jamais exécuter** de commande qui modifie git ou le remote :

- `git commit`, `git push`, `git add`
- `git reset`, `git rebase`, `git merge`, `git cherry-pick`, `git revert`
- `git stash` (push/pop/drop), création/suppression de branches, tags
- `gh pr create`, `gh repo create`, etc.

## Autorisé

Commandes **strictement en lecture** : `git status`, `git diff`, `git log`, `git show`, `gh pr view`, etc.

## Si l’utilisateur veut committer

1. Résumer les changements et proposer un message de commit **en texte**.
2. Donner les commandes pour qu’il les lance **lui-même** (ex. `git add … && git commit -m "…"`).
3. **Ne pas** lancer ces commandes dans le shell agent.

Référence : [HARNESS.md](../../../HARNESS.md) § Git.
