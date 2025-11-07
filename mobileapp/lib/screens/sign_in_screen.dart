import 'package:flutter/material.dart';
import 'package:mobileapp/l10n/app_localizations.dart';

import '../services/auth_service.dart';

class SignInScreen extends StatefulWidget {
  const SignInScreen({super.key});

  @override
  _SignInScreenState createState() => _SignInScreenState();
}

class _SignInScreenState extends State<SignInScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _authService = AuthService();

  Future<void> _signIn() async {
    if (_formKey.currentState!.validate()) {
      // try {
        final response = await _authService.signIn(
          email: _emailController.text,
          password: _passwordController.text,
        );

        if (response['key'] != null) {
          Navigator.pushReplacementNamed(context, '/home');
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                AppLocalizations.of(context)!.signInError,
              ),
            ),
          );
        }
      // } catch (e) {
      //   ScaffoldMessenger.of(context).showSnackBar(
      //     SnackBar(content: Text('Erreur: $e')),
      //   );
      // }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.signInTitle),
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
                controller: _passwordController,
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
              ElevatedButton(
                onPressed: _signIn,
                child: Text(AppLocalizations.of(context)!.signInButton),
              ),
              TextButton(
                onPressed: () {
                  Navigator.pushNamed(context, '/signup');
                },
                child: Text(AppLocalizations.of(context)!.goToSignUp),
              ),
            ],
          ),
        ),
      ),
    );
  }
}