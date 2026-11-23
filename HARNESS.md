# Harnais agent COSQUA (Cursor + Claude)

Ce dépôt embarque un **harnais** : règles, skills et hooks qui orientent les agents IA (Cursor Agent, Claude Code, CI `@claude`) vers les mêmes conventions, sans dupliquer toute la doc métier déjà présente dans `AGENTS.md` / `CLAUDE.md`.

## Objectifs

1. **Un seul référentiel** pour les workflows agent (skills, manifeste, hooks).
2. **Compatibilité Cursor et Claude** : les skills vivent sous `agents/skills/` ; Cursor les charge via `.cursor/skills` (lien symbolique).
3. **Délégation aux modèles adaptés** : les tâches simples ne doivent pas consommer le modèle le plus capable.
4. **Maintenance automatique** : après modification de fichiers « structurants », l’agent doit vérifier si le harnais doit être mis à jour (hook + skill `harness-sync`).
5. **Git en lecture seule** : l’agent **ne lance jamais** de commande git (ni `gh`) qui modifie le dépôt — **pas de `commit`, pas de `push`**, pas de `add`, rebase, merge, etc.

## Git : lecture seule (obligatoire)

L’agent **ne doit pas** exécuter de commandes git ou GitHub CLI qui écrivent dans le dépôt ou sur le remote. Les commits et pushes sont **réservés à l’humain**.

| Autorisé (exemples)                                                   | Interdit                                                                |
| --------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `git status`, `git diff`, `git log`, `git show`, `git branch` (liste) | `git commit`, `git push`, `git add`                                     |
| `git rev-parse`, `git merge-base`, `git blame` (lecture)              | `git reset`, `git rebase`, `git merge`, `git cherry-pick`, `git revert` |
| `gh pr view`, `gh run list` (lecture)                                 | `gh pr create`, `gh repo create`                                        |

**Cursor** : le hook `beforeShellExecution` (`git-no-write.sh`) bloque ces commandes.

**Claude Code** : même règle sans hook — ne pas contourner en shell.

Si l’utilisateur veut versionner : indiquer les commandes à lancer **localement**, sans les exécuter.

Voir [agents/skills/no-git-writes/SKILL.md](agents/skills/no-git-writes/SKILL.md).

## Arborescence

```
brico/
├── HARNESS.md                    # Ce fichier — point d’entrée du harnais
├── agents/
│   ├── harness-manifest.json     # Fichiers du harnais + déclencheurs de mise à jour
│   └── skills/                   # Skills projet (source unique)
├── .cursor/
│   ├── hooks.json                # Hooks Cursor (session, post-édition, sous-agents)
│   ├── hooks/*.sh                # Scripts de hook
│   ├── rules/*.mdc               # Règles Cursor persistantes
│   └── skills → ../agents/skills # Symlink vers agents/skills
├── AGENTS.md / CLAUDE.md         # Vue monorepo (+ renvoi ici)
├── webapp/AGENTS.md              # Détail webapp
├── mobileapp/AGENTS.md           # Détail mobile
└── docs/AGENTS.md                  # Détail docs
```

## Délégation : modèles et sous-agents

**Principe** : réserver le modèle principal (conversation en cours) aux décisions d’architecture, aux changements transverses et aux bugs ambigus. Déléguer le reste à des **modèles plus légers** ou à des **sous-agents spécialisés**, dès que la tâche est bien bornée et que le risque est faible.

| Type de tâche                                                 | Délégation recommandée                                                  | Pourquoi                         |
| ------------------------------------------------------------- | ----------------------------------------------------------------------- | -------------------------------- |
| Recherche de fichiers, « où est X ? », cartographie rapide    | Sous-agent `explore` (modèle rapide / thoroughness `quick` ou `medium`) | Lecture seule, pas de design     |
| Lint, format, commandes Make ciblées, tests d’un fichier      | Shell + modèle rapide si disponible ; pas de refactor « au passage »    | Mécanique, vérifiable            |
| Investigation CI sur une PR                                   | Sous-agent `ci-investigator`                                            | Périmètre étroit                 |
| Revue sécurité / Bugbot explicite                             | Skills dédiés ou sous-agents `security-review` / `bugbot`               | Expertise, pas le flux principal |
| Nouvelle feature, changement de modèle de données, auth, perf | **Modèle principal** + lire le `AGENTS.md` du composant                 | Impact et trade-offs             |

**Cursor** : utiliser l’outil Task avec le `subagent_type` approprié et, quand l’UI le permet, un modèle **fast** pour `explore` et les validations mécaniques.

**Claude Code** : même logique — prompts courts, lecture ciblée, éviter d’explorer tout le monorepo dans le thread principal ; documenter le plan puis exécuter.

**Anti-patterns** : utiliser le modèle le plus puissant pour renommer une variable, reformater, ou lister des endpoints ; enchaîner 50 lectures sans sous-agent d’exploration.

Voir le skill [agents/skills/delegate-tasks/SKILL.md](agents/skills/delegate-tasks/SKILL.md).

## Skills projet

| Skill            | Quand l’utiliser                                                   |
| ---------------- | ------------------------------------------------------------------ |
| `delegate-tasks` | Avant de lancer un gros travail — choisir modèle / sous-agent      |
| `harness-sync`   | Après changement Makefile, settings, nouvelle app, dépendances, CI |
| `cosqua-webapp`  | Travail dans `webapp/` (Django, Hotwire, tests)                    |
| `cosqua-mobile`  | Travail dans `mobileapp/` (Flutter)                                |
| `cosqua-docs`    | Travail dans `docs/` (Sphinx)                                      |
| `no-git-writes`  | Avant toute commande `git` / `gh` — lecture seule uniquement       |

## Hooks Cursor

Configurés dans [.cursor/hooks.json](.cursor/hooks.json) :

| Événement                              | Rôle                                                                 |
| -------------------------------------- | -------------------------------------------------------------------- |
| `sessionStart`                         | Rappel : lire `HARNESS.md`, politique de délégation, composant cible |
| `postToolUse` (`Write` / `StrReplace`) | Vérifie si le fichier modifié impose une mise à jour du harnais      |
| `subagentStart`                        | Rappel de délégation selon le type de sous-agent                     |
| `beforeShellExecution` (`git` / `gh`)  | Refuse commit, push, add et autres écritures git/gh                  |

Claude Code n’exécute pas ces hooks localement ; les mêmes règles sont dans ce fichier et dans la règle Cursor `harness-governance.mdc` — **à appliquer manuellement** après des edits importants.

## Quand mettre à jour le harnais

Dès qu’un changement touche :

- Commandes Make, `pyproject.toml`, `package.json`, `pubspec.yaml`
- `core/settings.py`, nouvelle app Django, URLs racine
- `docker-compose.yml`, workflows `.github/workflows/`
- Conventions documentées dans `*/AGENTS.md`

**Actions possibles** : mettre à jour `agents/harness-manifest.json`, le skill concerné, `.cursor/rules/*.mdc`, et les sections pertinentes de `AGENTS.md`.

Le hook `harness-sync-check` renvoie un rappel dans le contexte agent ; l’agent doit **proposer** les mises à jour, pas les ignorer.

Détail : skill [harness-sync](agents/skills/harness-sync/SKILL.md) et manifeste [agents/harness-manifest.json](agents/harness-manifest.json).

## Checklist agent (fin de tâche)

- [ ] Tests / lint du composant touché (`make test`, etc.)
- [ ] Si fichier structurant modifié : harnais à jour ou explicitement « non nécessaire »
- [ ] Tâches simples bien déléguées (pas de surconsommation du modèle principal)
- [ ] Diff minimal, code en anglais
- [ ] Aucune commande git/gh en écriture exécutée par l’agent

## Évolution du harnais

Pour ajouter un skill : `agents/skills/<nom>/SKILL.md` (voir skill Cursor `create-skill`). Pour une nouvelle règle Cursor : `.cursor/rules/<nom>.mdc`. Enregistrer les nouveaux chemins dans `harness-manifest.json`.
