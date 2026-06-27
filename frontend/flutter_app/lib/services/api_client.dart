import 'dart:convert';

import 'package:http/http.dart' as http;

/// Thrown when the backend returns a non-success status code.
class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException(this.statusCode, this.message);

  @override
  String toString() => message;
}

/// Thin HTTP wrapper that attaches the bearer token and decodes JSON,
/// surfacing FastAPI error details as [ApiException]s.
class ApiClient {
  ApiClient({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;
  String? _token;

  void setToken(String? token) => _token = token;

  Map<String, String> _headers({bool json = true}) => {
        if (json) 'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Future<dynamic> get(String url) async {
    final res = await _client.get(Uri.parse(url), headers: _headers());
    return _decode(res);
  }

  Future<dynamic> postJson(String url, Map<String, dynamic> body) async {
    final res = await _client.post(
      Uri.parse(url),
      headers: _headers(),
      body: jsonEncode(body),
    );
    return _decode(res);
  }

  Future<dynamic> postForm(String url, Map<String, String> fields) async {
    final res = await _client.post(
      Uri.parse(url),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        if (_token != null) 'Authorization': 'Bearer $_token',
      },
      body: fields,
    );
    return _decode(res);
  }

  Future<void> delete(String url) async {
    final res = await _client.delete(Uri.parse(url), headers: _headers());
    _decode(res);
  }

  dynamic _decode(http.Response res) {
    final bodyText = res.body.isEmpty ? '{}' : res.body;
    dynamic decoded;
    try {
      decoded = jsonDecode(bodyText);
    } catch (_) {
      decoded = bodyText;
    }
    if (res.statusCode >= 200 && res.statusCode < 300) {
      return decoded;
    }
    throw ApiException(res.statusCode, _extractDetail(decoded, res.statusCode));
  }

  String _extractDetail(dynamic decoded, int status) {
    if (decoded is Map && decoded['detail'] != null) {
      final detail = decoded['detail'];
      if (detail is String) return detail;
      if (detail is List && detail.isNotEmpty) {
        final first = detail.first;
        if (first is Map && first['msg'] != null) {
          return first['msg'].toString();
        }
      }
    }
    return 'Request failed (HTTP $status)';
  }
}
