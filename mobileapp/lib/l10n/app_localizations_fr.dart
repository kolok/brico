// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for French (`fr`).
class AppLocalizationsFr extends AppLocalizations {
  AppLocalizationsFr([String locale = 'fr']) : super(locale);

  @override
  String get appTitle => 'Démo Auth Flutter';

  @override
  String get signInTitle => 'Connexion';

  @override
  String get signInError => 'Erreur de connexion';

  @override
  String get emailLabel => 'Email';

  @override
  String get emailRequired => 'Veuillez entrer votre email';

  @override
  String get passwordLabel => 'Mot de passe';

  @override
  String get passwordRequired => 'Veuillez entrer votre mot de passe';

  @override
  String get signInButton => 'Se connecter';

  @override
  String get goToSignUp => 'Créer un compte';

  @override
  String get signUpTitle => 'Inscription';

  @override
  String get signUpError => 'Erreur d\'inscription';

  @override
  String genericError(String error) {
    return 'Erreur : $error';
  }

  @override
  String get confirmEmailLabel => 'Confirmer l\'email';

  @override
  String get confirmEmailRequired => 'Veuillez confirmer votre email';

  @override
  String get emailMismatch => 'Les adresses email ne correspondent pas';

  @override
  String get confirmPasswordLabel => 'Confirmer le mot de passe';

  @override
  String get confirmPasswordRequired => 'Veuillez confirmer votre mot de passe';

  @override
  String get passwordMismatch => 'Les mots de passe ne correspondent pas';

  @override
  String get signUpButton => 'S\'inscrire';

  @override
  String get logout => 'Déconnexion';

  @override
  String logoutError(String error) {
    return 'Erreur lors de la déconnexion : $error';
  }

  @override
  String get welcomeTitle => 'Bienvenue sur Brico !';

  @override
  String get welcomeSubtitle =>
      'Votre assistant pour tous vos projets de bricolage';
}
