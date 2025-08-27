import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class HomeScreen extends StatelessWidget {
  final AuthService authService = AuthService();

  HomeScreen({Key? key}) : super(key: key);

  void _handleLogout(BuildContext context) async {
    try {
      await authService.signOut();
      Navigator.pushReplacementNamed(context, '/signin');
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur lors de la déconnexion: $e')),
      );
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
            label: const Text(
              'Déconnexion',
              style: TextStyle(color: Colors.blue),
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
            children: const [
              Icon(
                Icons.home_repair_service,
                size: 80.0,
                color: Colors.blue,
              ),
              SizedBox(height: 20),
              Text(
                'Bienvenue sur Brico !',
                style: TextStyle(
                  fontSize: 24.0,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 10),
              Text(
                'Votre assistant pour tous vos projets de bricolage',
                textAlign: TextAlign.center,
                style: TextStyle(
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
