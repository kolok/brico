## Brico – Notes projet

### Vue d’ensemble

- Deux applications : `webapp/` (Django) et `mobileapp/` (Flutter).
- Services communs : base PostgreSQL via `docker-compose.yml` (`docker compose up -d`).
- Chaque sous-projet possède son `Makefile` avec les tâches de dev/build/test.

### Webapp (`webapp/`)

- **Backend** : Django 5 + Django REST Framework, auth via `django-allauth` / `dj-rest-auth`.
- **Gestion Python** : `uv` (Python ≥ 3.12). `make init-dev` configure l’environnement, `make sync` installe les deps, `make migrate` applique les migrations.
- **Exécution** : `make run` (Honcho + `Procfile.dev`), `make run-all` lance Docker puis l’appli.
- **Tests & qualité** : `make test` (pytest), `make lint` (ruff), `make format` (black).
- **i18n** : `make makemessages` et `make compilemessages`, fichiers dans `locale/fr/LC_MESSAGES/`.

#### Frontend associé

- **Bundler** : Parcel (scripts `npm run build/watch/lint` dans `package.json`).
- **Langages** : TypeScript + CSS/Tailwind. Entrées principales dans `static/to_compile/entrypoints/` (`main.ts`, `main.css`).
- **Organisation des assets** :
  - `static/to_compile/` : code à transpiler (TS/CSS).
  - `static/to_collect/` : assets copiés tels quels.
  - `static/compiled/` : sortie Parcel, nettoyée par `make clean`.
- **Hotwire** : utilisation de Stimulus + Turbo Frames.

### Mobile (`mobileapp/`)

- **Stack** : Flutter (SDK ≥ 3.3.1), projet multi-plateforme (Android/iOS/Web/Desktop).
- **Installation** : `flutter pub get` (ou `make install`).
- **Exécution** : `flutter run` (`make run`), `make hot-reload` pour le mode debug.
- **Qualité** : `make analyze`, `make format`, `make test`, `make lint`.
- **Builds** : cibles dédiées (`make build-android[-apk|-aab]`, `make build-ios`, `make build-web`, `make build-all`).

### Références rapides

- Root README : instructions Docker communes.
- `webapp/README.md` : onboarding UV/Django + gestion des traductions.
- `mobileapp/README.md` : prérequis Flutter & commandes de base.
