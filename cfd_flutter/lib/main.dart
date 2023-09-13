import 'package:cfd/registration_page.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:cfd/login_page.dart';
import 'home_page.dart';

void main() async {
  final bool isAuthenticated = await checkAuthentication();
  runApp(MyApp(isAuthenticated: isAuthenticated));
}

Future<bool> checkAuthentication() async {
  // Make an HTTP request to your server to check for the token in cookies.
  final response = await http.get(Uri.parse('https://bancolombias-url-fraud-detection.onrender.com/auth/authenticated'));
  if (response.statusCode == 200) {
    // If the server responds with a 200 status code, the user is authenticated.
    return true;
  } else {
    // If the server responds with an error status code, the user is not authenticated.
    return false;
  }
}

class MyApp extends StatelessWidget {
  final bool isAuthenticated;
  const MyApp({Key? key, required this.isAuthenticated}) : super(key: key);
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Detección del fraude de tajetas con phishing',
      debugShowCheckedModeBanner: false,
      initialRoute: '/',
      routes: {
        '/': (context) => HomePage(isAuthenticated: isAuthenticated),
        '/register': (context) => RegistrationPage(),
        '/login': (context) => LoginPage()
      },
    );
  }
}