import '../config/api_config.dart';
import '../models/document.dart';
import 'api_client.dart';

class DocumentService {
  DocumentService(this._api);
  final ApiClient _api;

  Future<List<Document>> list() async {
    final data = await _api.get('${ApiConfig.apiV1}/documents');
    return (data as List<dynamic>)
        .map((d) => Document.fromJson(d as Map<String, dynamic>))
        .toList();
  }

  Future<DocumentDetail> get(int id) async {
    final data = await _api.get('${ApiConfig.apiV1}/documents/$id');
    return DocumentDetail.fromJson(data as Map<String, dynamic>);
  }

  Future<Document> upload({
    required String filename,
    required List<int> bytes,
  }) async {
    final data = await _api.postMultipartFile(
      '${ApiConfig.apiV1}/documents',
      fieldName: 'file',
      filename: filename,
      bytes: bytes,
    );
    return Document.fromJson(data as Map<String, dynamic>);
  }

  Future<DocumentDetail> analyze(int id) async {
    final data =
        await _api.postJson('${ApiConfig.apiV1}/documents/$id/analyze', {});
    return DocumentDetail.fromJson(data as Map<String, dynamic>);
  }

  Future<void> delete(int id) async {
    await _api.delete('${ApiConfig.apiV1}/documents/$id');
  }
}
