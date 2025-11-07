// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Flutter Auth Demo';

  @override
  String get signInTitle => 'Sign In';

  @override
  String get signInError => 'Sign-in error';

  @override
  String get emailLabel => 'Email';

  @override
  String get emailRequired => 'Please enter your email';

  @override
  String get passwordLabel => 'Password';

  @override
  String get passwordRequired => 'Please enter your password';

  @override
  String get signInButton => 'Sign In';

  @override
  String get goToSignUp => 'Create an account';

  @override
  String get signUpTitle => 'Sign Up';

  @override
  String get signUpError => 'Sign-up error';

  @override
  String genericError(String error) {
    return 'Error: $error';
  }

  @override
  String get confirmEmailLabel => 'Confirm email';

  @override
  String get confirmEmailRequired => 'Please confirm your email';

  @override
  String get emailMismatch => 'Email addresses do not match';

  @override
  String get confirmPasswordLabel => 'Confirm password';

  @override
  String get confirmPasswordRequired => 'Please confirm your password';

  @override
  String get passwordMismatch => 'Passwords do not match';

  @override
  String get signUpButton => 'Sign Up';

  @override
  String get logout => 'Log out';

  @override
  String logoutError(String error) {
    return 'Error during logout: $error';
  }

  @override
  String get welcomeTitle => 'Welcome to Brico!';

  @override
  String get welcomeSubtitle => 'Your assistant for all your DIY projects';
}
