import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/user.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';

enum AuthStatus { unknown, authenticated, unauthenticated }

/// Owns the auth token + current user and keeps the [ApiClient] authorized.
class AuthProvider extends ChangeNotifier {
  AuthProvider({required ApiClient apiClient, required AuthService authService})
      : _api = apiClient,
        _auth = authService;

  static const _tokenKey = 'auth_token';

  final ApiClient _api;
  final AuthService _auth;

  AuthStatus _status = AuthStatus.unknown;
  User? _user;

  AuthStatus get status => _status;
  User? get user => _user;

  /// Restores a saved session on app start.
  Future<void> loadSession() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(_tokenKey);
    if (token == null || token.isEmpty) {
      _setUnauthenticated();
      notifyListeners();
      return;
    }
    _api.setToken(token);
    try {
      _user = await _auth.me();
      _status = AuthStatus.authenticated;
    } catch (_) {
      // Token expired or invalid — clear it.
      await _clearToken();
      _setUnauthenticated();
    }
    notifyListeners();
  }

  Future<void> login(String email, String password) async {
    final result = await _auth.login(email: email, password: password);
    await _applySession(result.token, result.user);
  }

  Future<void> register(String email, String fullName, String password) async {
    await _auth.register(email: email, fullName: fullName, password: password);
    // Registration does not return a token, so log in immediately after.
    await login(email, password);
  }

  Future<void> logout() async {
    await _clearToken();
    _api.setToken(null);
    _user = null;
    _setUnauthenticated();
    notifyListeners();
  }

  Future<void> _applySession(String token, User user) async {
    _user = user;
    _api.setToken(token);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
    _status = AuthStatus.authenticated;
    notifyListeners();
  }

  Future<void> _clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  void _setUnauthenticated() {
    _status = AuthStatus.unauthenticated;
  }
}
