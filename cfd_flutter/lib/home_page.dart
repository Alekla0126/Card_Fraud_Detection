import 'package:flutter/material.dart';

class HomePage extends StatelessWidget {
  final bool isAuthenticated;

  const HomePage({Key? key, required this.isAuthenticated}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detector de Phishing Bancolombia'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'Welcome!',
              style: TextStyle(
                fontSize: 24.0,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20.0),
            if (!isAuthenticated) ...[
              ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pushNamed('/login');
                },
                child: const Text('Login'),
              ),
              const SizedBox(height: 10.0),
              ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pushNamed('/register');
                },
                child: const Text('Register'),
              ),
            ],
            if (isAuthenticated) ...[
              ElevatedButton(
                onPressed: () {
                  // Implement logout logic here.
                },
                child: const Text('Logout'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}