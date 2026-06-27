import '../config/api_config.dart';
import '../models/rag.dart';
import 'api_client.dart';

class RagService {
  RagService(this._api);
  final ApiClient _api;

  Future<RagAnswer> ask(
    String question, {
    List<int>? documentIds,
    int? topK,
  }) async {
    final data = await _api.postJson('${ApiConfig.apiV1}/rag/ask', {
      'question': question,
      'document_ids': ?documentIds,
      'top_k': ?topK,
    });
    return RagAnswer.fromJson(data as Map<String, dynamic>);
  }
}
