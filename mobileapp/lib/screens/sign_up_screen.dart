import 'package:flutter/material.dart';

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
          // Navigation vers l'écran principal après inscription réussie
          Navigator.pushReplacementNamed(context, '/home');
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Erreur d\'inscription')),
          );
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erreur: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Inscription')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _emailController,
                decoration: InputDecoration(labelText: 'Email'),
                validator: (value) {
                  if (value?.isEmpty ?? true) {
                    return 'Veuillez entrer votre email';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: _emailConfirmationController,
                decoration: InputDecoration(labelText: 'Confirmer l\'email'),
                validator: (value) {
                  if (value?.isEmpty ?? true) {
                    return 'Veuillez confirmer votre email';
                  }
                  if (value != _emailController.text) {
                    return 'Les adresses email ne correspondent pas';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: _password1Controller,
                decoration: InputDecoration(labelText: 'Mot de passe'),
                obscureText: true,
                validator: (value) {
                  if (value?.isEmpty ?? true) {
                    return 'Veuillez entrer votre mot de passe';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: _password2Controller,
                decoration: InputDecoration(labelText: 'Confirmer le mot de passe'),
                obscureText: true,
                validator: (value) {
                  if (value?.isEmpty ?? true) {
                    return 'Veuillez confirmer votre mot de passe';
                  }
                  if (value != _password1Controller.text) {
                    return 'Les mots de passe ne correspondent pas';
                  }
                  return null;
                },
              ),
              ElevatedButton(
                onPressed: _signUp,
                child: Text('S\'inscrire'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}