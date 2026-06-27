import 'package:flutter/foundation.dart';

import '../models/chat_message.dart';
import '../models/conversation.dart';
import '../services/chat_service.dart';

/// Drives the active conversation: its message list and send/load state.
class ChatProvider extends ChangeNotifier {
  ChatProvider(this._chat);
  final ChatService _chat;

  final List<ChatMessage> _messages = [];
  List<ChatMessage> get messages => List.unmodifiable(_messages);

  int? _conversationId;
  int? get conversationId => _conversationId;

  bool _sending = false;
  bool get sending => _sending;

  bool _loading = false;
  bool get loading => _loading;

  String? _error;
  String? get error => _error;

  /// Resets to a fresh, empty conversation.
  void startNew() {
    _conversationId = null;
    _messages.clear();
    _error = null;
    notifyListeners();
  }

  /// Loads an existing conversation's history.
  Future<void> openConversation(int id) async {
    _loading = true;
    _error = null;
    _messages.clear();
    notifyListeners();
    try {
      final detail = await _chat.getConversation(id);
      _conversationId = detail.id;
      _messages.addAll(detail.messages);
    } catch (e) {
      _error = e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<void> send(String text) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty || _sending) return;

    _sending = true;
    _error = null;

    // Optimistically show the user's message immediately.
    final optimistic = ChatMessage(
      id: -DateTime.now().millisecondsSinceEpoch,
      conversationId: _conversationId ?? 0,
      role: 'user',
      content: trimmed,
      createdAt: DateTime.now(),
    );
    _messages.add(optimistic);
    notifyListeners();

    try {
      final res = await _chat.sendMessage(trimmed, conversationId: _conversationId);
      _conversationId = res.conversation.id;
      // Replace the optimistic message with the server's, then append reply.
      _messages
        ..removeWhere((m) => m.id == optimistic.id)
        ..add(res.userMessage)
        ..add(res.assistantMessage);
    } catch (e) {
      _error = e.toString();
      _messages.removeWhere((m) => m.id == optimistic.id);
    } finally {
      _sending = false;
      notifyListeners();
    }
  }
}

/// Provider for the conversation list shown on the home screen.
class ConversationsProvider extends ChangeNotifier {
  ConversationsProvider(this._chat);
  final ChatService _chat;

  List<Conversation> _items = [];
  List<Conversation> get items => List.unmodifiable(_items);

  bool _loading = false;
  bool get loading => _loading;

  String? _error;
  String? get error => _error;

  Future<void> refresh() async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _items = await _chat.listConversations();
    } catch (e) {
      _error = e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<void> delete(int id) async {
    await _chat.deleteConversation(id);
    _items = _items.where((c) => c.id != id).toList();
    notifyListeners();
  }
}
