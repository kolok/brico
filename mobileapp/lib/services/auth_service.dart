import 'package:http/http.dart' as http;
import 'dart:convert';

class AuthService {
  final String baseUrl = 'http://10.0.2.2:8000'; // Pour l'émulateur Android
  
  Future<Map<String, dynamic>> signUp({
    required String username,
    required String email,
    required String password1,
    required String password2,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/auth/registration/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        // 'username': username,
        'email': email,
        'email2': email,
        'password1': password1,
        'password2': password2,
        // 'phone': '',
      }),
    );

    if (response.statusCode == 201 || response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Erreur d\'inscription: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> signIn({
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/auth/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Erreur de connexion: ${response.body}');
    }
  }

  Future<void> signOut() async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/auth/logout/'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode != 200) {
      throw Exception('Erreur lors de la déconnexion: ${response.body}');
    }
  }
} 