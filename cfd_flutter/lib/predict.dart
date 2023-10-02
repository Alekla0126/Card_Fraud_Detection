import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'dart:convert';

class UrlClassification extends StatefulWidget {
  @override
  _UrlClassificationState createState() => _UrlClassificationState();
}

class _UrlClassificationState extends State<UrlClassification> {
  final _urlController = TextEditingController();

  Future<void> sendData() async {
    final url = _urlController.text;
    if (url.isEmpty) {
      return;
    }
    try {
      final result = await performNetworkRequest(url);
      showResultDialog(result);
    } catch (error) {
      showErrorDialog(error);
    }
  }

  Future<Map<String, dynamic>> performNetworkRequest(String url) async {
    final response = await http.post(
      Uri.parse('https://bancolombias-url-fraud-detection.onrender.com/prediction'),
      body: json.encode({'URL': url}),
    );
    return json.decode(response.body);
  }

  void showResultDialog(Map<String, dynamic> result) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          content: Text(json.encode(result)),
        );
      },
    );
  }

  void showErrorDialog(Object error) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          content: Text('Error: $error'),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('URL Classification'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                labelText: 'URL',
              ),
              keyboardType: TextInputType.url,
            ),
            SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: sendData,
                child: Text('Predict'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}