import 'package:flutter/material.dart';
import 'package:mobileapp/l10n/app_localizations.dart';

import '../services/auth_service.dart';

class SignUpScreen extends StatefulWidget {
  const SignUpScreen({super.key});

  @override
  _SignUpScreenState createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _emailConfirmationController = TextEditingController();
  final _password1Controller = TextEditingController();
  final _password2Controller = TextEditingController();
  final _authService = AuthService();

  Future<void> _signUp() async {
    if (_formKey.currentState!.validate()) {
      try {
        final response = await _authService.signUp(
          email: _emailController.text,
          emailConfirmation: _emailConfirmationController.text,
          password1: _password1Controller.text,
          password2: _password2Controller.text,
        );

        if (response['key'] != null) {
          Navigator.pushReplacementNamed(context, '/home');
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(AppLocalizations.of(context)!.signUpError),
            ),
          );
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              AppLocalizations.of(context)!.genericError(
                e.toString(),
              ),
            ),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.signUpTitle),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _emailController,
                decoration: InputDecoration(
                  labelText: AppLocalizations.of(context)!.emailLabel,
                ),
                validator: (value) {
                  if (value?.isEmpty ?? true) {
                    return AppLocalizations.of(context)!.emailRequired;
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: _emailConfirmationController,
                decoration: InputDecoration(
                  labelText: AppLocalizations.of(context)!.confirmEmailLabel,
                ),
                validator: (value) {
                  if (value?.isEmpty ?? true) {
                    return AppLocalizations.of(context)!.confirmEmailRequired;
                  }
                  if (value != _emailController.text) {
                    return AppLocalizations.of(context)!.emailMismatch;
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: _password1Controller,
                decoration: InputDecoration(
                  labelText: AppLocalizations.of(context)!.passwordLabel,
                ),
                obscureText: true,
                validator: (value) {
                  if (value?.isEmpty ?? true) {
                    return AppLocalizations.of(context)!.passwordRequired;
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: _password2Controller,
                decoration: InputDecoration(
                  labelText:
                      AppLocalizations.of(context)!.confirmPasswordLabel,
                ),
                obscureText: true,
                validator: (value) {
                  if (value?.isEmpty ?? true) {
                    return AppLocalizations.of(context)!
                        .confirmPasswordRequired;
                  }
                  if (value != _password1Controller.text) {
                    return AppLocalizations.of(context)!.passwordMismatch;
                  }
                  return null;
                },
              ),
              ElevatedButton(
                onPressed: _signUp,
                child: Text(AppLocalizations.of(context)!.signUpButton),
              ),
            ],
          ),
        ),
      ),
    );
  }
}