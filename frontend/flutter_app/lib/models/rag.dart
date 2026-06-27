class RagSource {
  final int documentId;
  final int chunkIndex;
  final String snippet;

  const RagSource({
    required this.documentId,
    required this.chunkIndex,
    required this.snippet,
  });

  factory RagSource.fromJson(Map<String, dynamic> json) {
    return RagSource(
      documentId: json['document_id'] as int,
      chunkIndex: json['chunk_index'] as int,
      snippet: json['snippet'] as String? ?? '',
    );
  }
}

class RagAnswer {
  final String answer;
  final List<RagSource> sources;

  const RagAnswer({required this.answer, required this.sources});

  factory RagAnswer.fromJson(Map<String, dynamic> json) {
    final rawSources = json['sources'] as List<dynamic>? ?? [];
    return RagAnswer(
      answer: json['answer'] as String? ?? '',
      sources: rawSources
          .map((s) => RagSource.fromJson(s as Map<String, dynamic>))
          .toList(),
    );
  }
}
