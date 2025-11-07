# MobileApp

## Prerequis

- flutter

## Installation

```sh
flutter upgrade
flutter pub get
```

## Lancement de l'application

lancer un emulateur depuis

```sh
flutter run
```

## mise à jour des dépendances

```sh
flutter pub upgrade --major-versions
```

## Internationalisation

L’interface supporte l’anglais (par défaut) et le français via `flutter gen-l10n`.

- Modifier ou ajouter des traductions dans `lib/l10n/app_en.arb` et `lib/l10n/app_fr.arb`.
- Générer les fichiers de localisation avec :

```sh
flutter gen-l10n
```
