---
name: harness-sync
description: Determines whether COSQUA agent harness files must be updated after code changes. Use when editing Makefile, settings, dependencies, CI, new Django apps, or when the harness-sync hook fires.
---

# Synchronisation du harnais

## Quand appliquer ce skill

- Le hook `harness-sync-check` a ajouté un rappel au contexte.
- Vous venez de modifier un fichier listé dans [agents/harness-manifest.json](../../harness-manifest.json).
- Vous ajoutez une commande Make, une app, ou un workflow CI.

## Procédure

1. Lire `agents/harness-manifest.json` et identifier le `trigger` dont le `pattern` correspond au fichier modifié.
2. Pour chaque entrée dans `suggest_updates` :
   - Ouvrir le fichier ; vérifier commandes, chemins, conventions.
   - Mettre à jour si la doc ou le skill est obsolète.
3. Si le changement introduit un **nouveau type** de fichier structurant : ajouter un `trigger` au manifeste.
4. Si nouveau workflow agent récurrent : envisager un skill sous `agents/skills/<nom>/`.
5. Ne pas dupliquer `webapp/AGENTS.md` dans `HARNESS.md` — renvoyer vers le bon `AGENTS.md`.

## Fichiers du harnais (ne pas oublier)

- `HARNESS.md`
- `agents/harness-manifest.json`
- `agents/skills/**/SKILL.md`
- `.cursor/hooks.json`, `.cursor/hooks/*`
- `.cursor/rules/*.mdc`

## Sortie attendue

Si mise à jour nécessaire : faire les edits dans le **même PR / session** que le changement de code, ou signaler clairement à l’utilisateur ce qui reste à faire.

Si aucune mise à jour : une phrase de justification (ex. « rename interne, pas de changement de commandes »).
