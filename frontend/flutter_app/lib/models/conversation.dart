import 'chat_message.dart';

class Conversation {
  final int id;
  final String title;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Conversation({
    required this.id,
    required this.title,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      id: json['id'] as int,
      title: json['title'] as String? ?? 'Untitled',
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }
}

/// A conversation with its full message history (GET /chat/conversations/{id}).
class ConversationDetail extends Conversation {
  final List<ChatMessage> messages;

  const ConversationDetail({
    required super.id,
    required super.title,
    required super.createdAt,
    required super.updatedAt,
    required this.messages,
  });

  factory ConversationDetail.fromJson(Map<String, dynamic> json) {
    final rawMessages = (json['messages'] as List<dynamic>? ?? []);
    return ConversationDetail(
      id: json['id'] as int,
      title: json['title'] as String? ?? 'Untitled',
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      messages: rawMessages
          .map((m) => ChatMessage.fromJson(m as Map<String, dynamic>))
          .toList(),
    );
  }
}
