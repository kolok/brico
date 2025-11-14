import 'package:flutter/material.dart';
import 'package:mobileapp/l10n/app_localizations.dart';

import '../services/auth_service.dart';

class HomeScreen extends StatelessWidget {
  final AuthService authService = AuthService();

  HomeScreen({super.key});

  void _handleLogout(BuildContext context) async {
    try {
      await authService.signOut();
      Navigator.pushReplacementNamed(context, '/signin');
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(
          AppLocalizations.of(context)!.logoutError(
            e.toString(),
          ),
        ),
      ));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Brico'),
        actions: [
          TextButton.icon(
            icon: const Icon(Icons.logout, color: Colors.blue),
            label: Text(
              AppLocalizations.of(context)!.logout,
              style: const TextStyle(color: Colors.blue),
            ),
            onPressed: () => _handleLogout(context),
          ),
        ],
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.home_repair_service,
                size: 80.0,
                color: Colors.blue,
              ),
              const SizedBox(height: 20),
              Text(
                AppLocalizations.of(context)!.welcomeTitle,
                style: const TextStyle(
                  fontSize: 24.0,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                AppLocalizations.of(context)!.welcomeSubtitle,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 16.0,
                  color: Colors.grey,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
