import 'package:shared_preferences/shared_preferences.dart';
import 'package:dio_cookie_manager/dio_cookie_manager.dart';
import 'package:cookie_jar/cookie_jar.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'dart:convert';
import 'dart:core';


class PredictionPage extends StatefulWidget {
  @override
  _PredictionPageState createState() => _PredictionPageState();
}

class _PredictionPageState extends State<PredictionPage> {
  final TextEditingController urlController = TextEditingController();
  String predictionResult = '';
  final Dio dio = Dio();

  // Set up cookie jar and attach it to Dio
  final CookieJar cookieJar = CookieJar();
  final BaseOptions options = BaseOptions(
    baseUrl: 'https://bancolombias-url-fraud-detection.onrender.com',
    headers: {
      'Content-Type': 'application/json',
    },
    responseType: ResponseType.json,
  );

  @override
  void initState() {
    super.initState();
    dio.options = options;
    if (!kIsWeb) {
      dio.interceptors.add(CookieManager(cookieJar));
    }
  }

  Future<void> sendPredictionRequest(String url) async {
    try {
      final response = await dio.post(
        '/prediction/',
        data: jsonEncode({'URL': url}),
      );
      if (response.statusCode == 200) {
        final int prediction = response.data['prediction'];
        setState(() {
          predictionResult = 'Predicted Class: $prediction';
        });
      } else {
        print('HTTP Error: ${response.statusCode}');
        final String message = response.data['message'] ?? 'Prediction failed';
        setState(() {
          predictionResult = message;
        });
      }
    } catch (error) {
      // Handle network or other errors
      print('Error: $error');
      setState(() {
        predictionResult = 'Prediction failed';
      });
    }
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
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            const Text(
              'Enter URL to Classify',
              style: TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: urlController,
              decoration: const InputDecoration(
                labelText: 'URL',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  final url = urlController.text;
                  if (url.isNotEmpty) {
                    sendPredictionRequest(url);
                  }
                },
                child: const Text('Predict'),
              ),
            ),
            const SizedBox(height: 20),
            Text(
              predictionResult,
              style: const TextStyle(fontSize: 18),
            ),
          ],
        ),
      ),
    );
  }
}