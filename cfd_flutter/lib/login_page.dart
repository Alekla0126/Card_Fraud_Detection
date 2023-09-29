import 'package:shared_preferences/shared_preferences.dart';
import 'package:cfd_flutter/predict.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'http_client.dart';
import 'dart:convert';

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();

  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    prefs.setString('token', token);
  }


  Future<void> loginUser(String username, String password) async {
    final Uri uri = Uri.parse(
        'https://bancolombias-url-fraud-detection.onrender.com/auth/login');
    final response = await httpClient.send(http.Request('POST', uri)
      ..headers['Content-Type'] = 'application/json'
      ..body = jsonEncode({
        'username': username,
        'password': password,
      }));
    if (response.statusCode == 200) {
      final http.Response finalResponse = await http.Response.fromStream(response);
      Map<String, dynamic> responseData = jsonDecode(finalResponse.body);
      if (responseData['status'] == 'success') {
        // So, we can navigate to the PredictionPage directly.
        Navigator.of(context).pushNamed('/prediction');
      } else {
        print(responseData['message']);
      }
    } else {
      print('Request failed with status: ${response.statusCode}.');
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Inicio')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _usernameController,
              decoration: const InputDecoration(labelText: 'Username'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: 'Password'),
              obscureText: true,
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                child: const Text('Login'),
                onPressed: () {
                  String username = _usernameController.text;
                  String password = _passwordController.text;
                  loginUser(username, password);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
