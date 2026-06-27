import 'package:flutter/foundation.dart';

import '../models/document.dart';
import '../services/document_service.dart';

/// Owns the uploaded-document list plus upload/delete state.
class DocumentsProvider extends ChangeNotifier {
  DocumentsProvider(this._service);
  final DocumentService _service;

  List<Document> _items = [];
  List<Document> get items => List.unmodifiable(_items);

  bool _loading = false;
  bool get loading => _loading;

  bool _uploading = false;
  bool get uploading => _uploading;

  String? _error;
  String? get error => _error;

  Future<void> refresh() async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _items = await _service.list();
    } catch (e) {
      _error = e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  /// Uploads a file and refreshes the list. Returns true on success.
  Future<bool> upload({required String filename, required List<int> bytes}) async {
    _uploading = true;
    _error = null;
    notifyListeners();
    try {
      await _service.upload(filename: filename, bytes: bytes);
      await refresh();
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _uploading = false;
      notifyListeners();
    }
  }

  Future<void> delete(int id) async {
    await _service.delete(id);
    _items = _items.where((d) => d.id != id).toList();
    notifyListeners();
  }
}
