import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class RegistrationPage extends StatefulWidget {
  const RegistrationPage({super.key});
  @override
  _RegistrationPageState createState() => _RegistrationPageState();
}

class _RegistrationPageState extends State<RegistrationPage> {
  final TextEditingController usernameController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  String? _selectedTier; // Variable to keep track of the selected tier
  List<String> tiers = ['free', 'professional', 'enterprise']; // List of tiers available

  Future<void> registerUser(String username, String password, String tier) async {
    final Uri uri = Uri.parse('https://bancolombias-url-fraud-detection.onrender.com/auth/register');

    final response = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'username': username,
        'password': password,
        'tier': tier,  // Sending the tier to the server
      }),
    );

    if (response.statusCode == 200) {
      Map<String, dynamic> responseData = jsonDecode(response.body);
      if (responseData['status'] == 'success') {
        // Registration was successful
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: Text('Success'),
            content: Text(responseData['message']),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: Text('OK'),
              ),
            ],
          ),
        );
      } else {
        // Handle error response
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: Text('Error'),
            content: Text(responseData['message']),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: Text('OK'),
              ),
            ],
          ),
        );
      }
    } else {
      // Handle other unexpected HTTP responses
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('Error'),
          content: Text('Request failed with status: ${response.statusCode}.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Registration'),
      ),
      body: Form(
        key: _formKey,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              TextFormField(
                controller: usernameController,
                validator: (value) {
                  if (value!.isEmpty) {
                    return 'Username is required';
                  }
                  return null;
                },
                decoration: const InputDecoration(labelText: 'Username'),
              ),
              TextFormField(
                controller: passwordController,
                obscureText: true,
                validator: (value) {
                  if (value!.isEmpty) {
                    return 'Password is required';
                  }
                  return null;
                },
                decoration: const InputDecoration(labelText: 'Password'),
              ),
              DropdownButtonFormField(
                value: _selectedTier,
                onChanged: (value) {
                  setState(() {
                    _selectedTier = value;
                  });
                },
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please select a tier';
                  }
                  return null;
                },
                items: tiers.map((tier) {
                  return DropdownMenuItem(
                    value: tier,
                    child: Text(tier),
                  );
                }).toList(),
                decoration: const InputDecoration(labelText: 'Select Tier'),
              ),
              const SizedBox(height: 16),
              Container(
                width: double.infinity,
                child: ElevatedButton(
                onPressed: () {
                  if (_formKey.currentState!.validate()) {
                    registerUser(usernameController.text, passwordController.text, _selectedTier!);
                  }
                },
                child: const Text('Register'),
              ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}