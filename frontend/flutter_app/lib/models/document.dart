/// Processing status reported by the backend for an uploaded document.
enum DocumentStatus { pending, processing, processed, failed, unknown }

DocumentStatus _statusFrom(String? raw) {
  switch (raw) {
    case 'pending':
      return DocumentStatus.pending;
    case 'processing':
      return DocumentStatus.processing;
    case 'processed':
      return DocumentStatus.processed;
    case 'failed':
      return DocumentStatus.failed;
    default:
      return DocumentStatus.unknown;
  }
}

class Document {
  final int id;
  final String originalFilename;
  final String contentType;
  final String fileExtension;
  final int sizeBytes;
  final DocumentStatus status;
  final int? chunkCount;
  final String? error;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Document({
    required this.id,
    required this.originalFilename,
    required this.contentType,
    required this.fileExtension,
    required this.sizeBytes,
    required this.status,
    required this.chunkCount,
    required this.error,
    required this.createdAt,
    required this.updatedAt,
  });

  bool get isProcessed => status == DocumentStatus.processed;

  factory Document.fromJson(Map<String, dynamic> json) {
    return Document(
      id: json['id'] as int,
      originalFilename: json['original_filename'] as String? ?? 'file',
      contentType: json['content_type'] as String? ?? '',
      fileExtension: json['file_extension'] as String? ?? '',
      sizeBytes: json['size_bytes'] as int? ?? 0,
      status: _statusFrom(json['status'] as String?),
      chunkCount: json['chunk_count'] as int?,
      error: json['error'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }
}

/// A document with its extracted text and optional patient-friendly analysis.
class DocumentDetail extends Document {
  final String? extractedText;
  final String? analysis;

  const DocumentDetail({
    required super.id,
    required super.originalFilename,
    required super.contentType,
    required super.fileExtension,
    required super.sizeBytes,
    required super.status,
    required super.chunkCount,
    required super.error,
    required super.createdAt,
    required super.updatedAt,
    required this.extractedText,
    required this.analysis,
  });

  factory DocumentDetail.fromJson(Map<String, dynamic> json) {
    return DocumentDetail(
      id: json['id'] as int,
      originalFilename: json['original_filename'] as String? ?? 'file',
      contentType: json['content_type'] as String? ?? '',
      fileExtension: json['file_extension'] as String? ?? '',
      sizeBytes: json['size_bytes'] as int? ?? 0,
      status: _statusFrom(json['status'] as String?),
      chunkCount: json['chunk_count'] as int?,
      error: json['error'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      extractedText: json['extracted_text'] as String?,
      analysis: json['analysis'] as String?,
    );
  }
}
