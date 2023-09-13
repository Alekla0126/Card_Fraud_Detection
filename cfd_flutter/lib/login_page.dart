import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();

  Future<void> loginUser(String username, String password) async {
    final Uri uri = Uri.parse('https://bancolombias-url-fraud-detection.onrender.com/auth/login');

    final response = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      Map<String, dynamic> responseData = jsonDecode(response.body);

      if (responseData['status'] == 'success') {
        // Extracting the token from the headers
        String? rawCookie = response.headers['set-cookie'];

        if (rawCookie != null) {
          int index = rawCookie.indexOf(';');
          // The token will be saved as: token=YOUR_TOKEN_VALUE;
          String cookie = (index == -1) ? rawCookie : rawCookie.substring(0, index);
          // Now you can store the cookie or use it for subsequent requests.
          print(cookie);
        }

        // Show success dialog
        showDialog(
          context: context,
          builder: (BuildContext context) {
            return AlertDialog(
              title: Text('Success'),
              content: Text('Logged in successfully!'),
              actions: [
                TextButton(
                  child: Text('OK'),
                  onPressed: () {
                    Navigator.of(context).pop();
                  },
                ),
              ],
            );
          },
        );

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
      appBar: AppBar(title: const Text('Login')),
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
            ElevatedButton(
              child: const Text('Login'),
              onPressed: () {
                String username = _usernameController.text;
                String password = _passwordController.text;
                loginUser(username, password);
              },
            ),
          ],
        ),
      ),
    );
  }
}