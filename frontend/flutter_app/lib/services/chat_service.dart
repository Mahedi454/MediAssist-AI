import '../config/api_config.dart';
import '../models/chat_response.dart';
import '../models/conversation.dart';
import 'api_client.dart';

class ChatService {
  ChatService(this._api);
  final ApiClient _api;

  Future<List<Conversation>> listConversations() async {
    final data = await _api.get('${ApiConfig.apiV1}/chat/conversations');
    return (data as List<dynamic>)
        .map((c) => Conversation.fromJson(c as Map<String, dynamic>))
        .toList();
  }

  Future<ConversationDetail> getConversation(int id) async {
    final data =
        await _api.get('${ApiConfig.apiV1}/chat/conversations/$id');
    return ConversationDetail.fromJson(data as Map<String, dynamic>);
  }

  /// Sends a message. Pass [conversationId] to continue an existing thread,
  /// or null to start a new one.
  Future<ChatResponse> sendMessage(String message, {int? conversationId}) async {
    final data = await _api.postJson('${ApiConfig.apiV1}/chat/messages', {
      'message': message,
      'conversation_id': ?conversationId,
    });
    return ChatResponse.fromJson(data as Map<String, dynamic>);
  }

  Future<void> deleteConversation(int id) async {
    await _api.delete('${ApiConfig.apiV1}/chat/conversations/$id');
  }
}
