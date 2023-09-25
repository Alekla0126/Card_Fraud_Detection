import 'package:cookie_jar/cookie_jar.dart';
import 'package:http/http.dart' as http;

class MyHttpClient extends http.BaseClient {
  final http.Client _inner = http.Client();
  final CookieJar cookieJar = CookieJar();

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    // Load cookies for the request URI
    var cookies = await cookieJar.loadForRequest(request.url);
    request.headers['Cookie'] = cookies.map((cookie) => '${cookie.name}=${cookie.value}').join('; ');

    final response = await _inner.send(request);

    // Save cookies from the response
    var setCookieHeader = response.headers['set-cookie'];
    if (setCookieHeader != null) {
      var cookies = <Cookie>[];
      var setCookies = setCookieHeader.split(', ');
      for (var setCookie in setCookies) {
        cookies.add(Cookie.fromSetCookieValue(setCookie));
      }
      cookieJar.saveFromResponse(request.url, cookies);
    }

    return response;
  }
}

final httpClient = MyHttpClient();