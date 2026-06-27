import 'package:flutter/foundation.dart';

/// Central configuration for talking to the MediAssist AI backend.
///
/// The base URL differs by platform when running locally:
/// - Web/desktop reach the host directly on `localhost`.
/// - The Android emulator maps the host machine to `10.0.2.2`.
///
/// Override at build/run time with `--dart-define=API_BASE_URL=...`.
class ApiConfig {
  static const String _override =
      String.fromEnvironment('API_BASE_URL', defaultValue: '');

  static String get baseUrl {
    if (_override.isNotEmpty) return _override;
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000';
    }
    return 'http://localhost:8000';
  }

  static String get apiV1 => '$baseUrl/api/v1';
}
