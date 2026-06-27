import 'conversation.dart';
import 'document.dart';

class DashboardStatistics {
  final int totalConversations;
  final int totalMessages;
  final int totalDocuments;
  final int processedDocuments;
  final int totalChunks;

  const DashboardStatistics({
    required this.totalConversations,
    required this.totalMessages,
    required this.totalDocuments,
    required this.processedDocuments,
    required this.totalChunks,
  });

  factory DashboardStatistics.fromJson(Map<String, dynamic> json) {
    return DashboardStatistics(
      totalConversations: json['total_conversations'] as int? ?? 0,
      totalMessages: json['total_messages'] as int? ?? 0,
      totalDocuments: json['total_documents'] as int? ?? 0,
      processedDocuments: json['processed_documents'] as int? ?? 0,
      totalChunks: json['total_chunks'] as int? ?? 0,
    );
  }
}

class Dashboard {
  final DashboardStatistics statistics;
  final List<Document> recentUploads;
  final List<Conversation> recentChats;

  const Dashboard({
    required this.statistics,
    required this.recentUploads,
    required this.recentChats,
  });

  factory Dashboard.fromJson(Map<String, dynamic> json) {
    return Dashboard(
      statistics: DashboardStatistics.fromJson(
          json['statistics'] as Map<String, dynamic>),
      recentUploads: (json['recent_uploads'] as List<dynamic>? ?? [])
          .map((d) => Document.fromJson(d as Map<String, dynamic>))
          .toList(),
      recentChats: (json['recent_chats'] as List<dynamic>? ?? [])
          .map((c) => Conversation.fromJson(c as Map<String, dynamic>))
          .toList(),
    );
  }
}
