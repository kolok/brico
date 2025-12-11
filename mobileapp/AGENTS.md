# MobileApp Agent Notes (Flutter)

## Scope

This file applies to **`mobileapp/` only**.

## High-level map

- App source: `lib/`
- Tests: `test/`
- Localizations:
  - ARB files: `lib/l10n/app_en.arb`, `lib/l10n/app_fr.arb`
  - Config: `l10n.yaml`
  - Generated via: `flutter gen-l10n`

## Default workflow (follow this)

1. **Explore**: locate the widget/page/service involved and read existing tests.
2. **Plan**: propose the smallest change that keeps UI behavior consistent across platforms.
3. **Implement**:
   - Prefer **immutable widgets** and official Dart conventions.
   - Keep business logic testable (avoid embedding logic deep in widgets).
4. **Verify**:
   - Run unit/widget tests.
   - Run analyzer + formatting checks.
   - If localization changed, regenerate l10n.

## Code Standards

- Flutter: official Dart conventions, prefer immutable widgets.
- Language: the application and documentation are all in English

## Commands (use Make targets first)

- **Install deps**: `make install` (flutter pub get)
- **Run**: `make run`
- **Hot reload**: `make hot-reload`
- **Tests**: `make test` (or `make test-coverage`)
- **Static analysis**: `make analyze`
- **Format**:
  - Apply: `make format`
  - Check: `make check-format`
- **All checks**: `make lint` (analyze + check-format)
- **Localizations**: `make localizations` (runs `flutter gen-l10n`)
- **Builds**:
  - Android APK: `make build-android-apk`
  - Android AAB: `make build-android-aab`
  - Web: `make build-web`
  - All: `make build-all`

## Internationalization (i18n)

- The UI supports **English (default)** and **French**.
- When editing ARB files, always run `make localizations` and ensure no missing keys.
- Prefer **stable message keys** (avoid renaming keys without a migration plan).

## Code quality rules

- Keep `dart format` line length at **120** (as configured in the Makefile).
- Avoid printing/logging in production code (keep logs behind debug flags if needed).
- Add tests for non-trivial logic and for UI regressions when feasible.

## Repo hygiene

- Do not commit generated or platform-specific artifacts unless explicitly required.
- For release builds/signing, follow the Makefile notes (Android keystore, iOS provisioning).
