import 'chat_message.dart';
import 'conversation.dart';

/// Response from POST /chat/messages.
class ChatResponse {
  final Conversation conversation;
  final ChatMessage userMessage;
  final ChatMessage assistantMessage;

  const ChatResponse({
    required this.conversation,
    required this.userMessage,
    required this.assistantMessage,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      conversation:
          Conversation.fromJson(json['conversation'] as Map<String, dynamic>),
      userMessage:
          ChatMessage.fromJson(json['user_message'] as Map<String, dynamic>),
      assistantMessage: ChatMessage.fromJson(
          json['assistant_message'] as Map<String, dynamic>),
    );
  }
}
