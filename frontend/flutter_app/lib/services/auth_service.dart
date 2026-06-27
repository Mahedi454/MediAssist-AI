import '../config/api_config.dart';
import '../models/user.dart';
import 'api_client.dart';

class AuthResult {
  final String token;
  final User user;
  const AuthResult({required this.token, required this.user});
}

class AuthService {
  AuthService(this._api);
  final ApiClient _api;

  Future<User> register({
    required String email,
    required String fullName,
    required String password,
  }) async {
    final data = await _api.postJson('${ApiConfig.apiV1}/auth/register', {
      'email': email,
      'full_name': fullName,
      'password': password,
    });
    return User.fromJson(data as Map<String, dynamic>);
  }

  Future<AuthResult> login({
    required String email,
    required String password,
  }) async {
    // The backend uses an OAuth2 form login: the email goes in `username`.
    final data = await _api.postForm('${ApiConfig.apiV1}/auth/login', {
      'username': email,
      'password': password,
    });
    final map = data as Map<String, dynamic>;
    return AuthResult(
      token: map['access_token'] as String,
      user: User.fromJson(map['user'] as Map<String, dynamic>),
    );
  }

  Future<User> me() async {
    final data = await _api.get('${ApiConfig.apiV1}/auth/me');
    return User.fromJson(data as Map<String, dynamic>);
  }
}
