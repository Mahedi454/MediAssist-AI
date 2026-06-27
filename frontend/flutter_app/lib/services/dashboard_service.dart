import '../config/api_config.dart';
import '../models/dashboard.dart';
import 'api_client.dart';

class DashboardService {
  DashboardService(this._api);
  final ApiClient _api;

  Future<Dashboard> get() async {
    final data = await _api.get('${ApiConfig.apiV1}/dashboard');
    return Dashboard.fromJson(data as Map<String, dynamic>);
  }
}
