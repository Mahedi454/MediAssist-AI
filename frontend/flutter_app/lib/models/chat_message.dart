class ChatMessage {
  final int id;
  final int conversationId;
  final String role; // "user" or "assistant"
  final String content;
  final DateTime createdAt;

  const ChatMessage({
    required this.id,
    required this.conversationId,
    required this.role,
    required this.content,
    required this.createdAt,
  });

  bool get isUser => role == 'user';

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] as int,
      conversationId: json['conversation_id'] as int,
      role: json['role'] as String,
      content: json['content'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
