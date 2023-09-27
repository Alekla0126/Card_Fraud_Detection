import 'package:dio_cookie_manager/dio_cookie_manager.dart';
import 'package:cookie_jar/cookie_jar.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'dart:html' as html;
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
  // final CookieJar cookieJar = CookieJar();
  // final BaseOptions options = BaseOptions(
  //   baseUrl: 'https://bancolombias-url-fraud-detection.onrender.com',
  //   headers: {
  //     'Content-Type': 'application/json',
  //   },
  //   responseType: ResponseType.json,
  // );

  // String? getTokenFromCookies() {
  //   String? cookies = html.document.cookie;
  //   List<String>? cookieList = cookies?.split(';');
  //   for (var cookie in cookieList!) {
  //     List<String> cookieParts = cookie.split('=');
  //     if (cookieParts[0].trim() == 'token') {
  //       return cookieParts[1].trim();
  //     }
  //   }
  //   return null;
  // }

  @override
  void initState() {
    super.initState();
    // dio.options = options;
    // if (!kIsWeb) {
    //   dio.interceptors.add(CookieManager(cookieJar));
    // }
  }

  Future<void> sendPredictionRequest(String url) async {
    try {

      final response = await dio.post(
        '/prediction/',
        data: jsonEncode({'URL': url}),
        options: Options(
          headers: {
            'Content-Type': 'application/json',
          },
          extra: {
            'withCredentials': true,
          },
        ),
      );
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