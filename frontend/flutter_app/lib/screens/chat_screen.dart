import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/chat_message.dart';
import '../state/chat_provider.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    final text = _controller.text;
    if (text.trim().isEmpty) return;
    _controller.clear();
    await context.read<ChatProvider>().send(text);
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final chat = context.watch<ChatProvider>();

    // Keep the view pinned to the newest message as it grows.
    if (chat.messages.isNotEmpty) _scrollToBottom();

    return Scaffold(
      appBar: AppBar(title: const Text('Chat')),
      body: Column(
        children: [
          if (chat.error != null)
            Container(
              width: double.infinity,
              color: Theme.of(context).colorScheme.errorContainer,
              padding: const EdgeInsets.all(12),
              child: Text(chat.error!,
                  style: TextStyle(
                      color: Theme.of(context).colorScheme.onErrorContainer)),
            ),
          Expanded(child: _buildMessages(chat)),
          if (chat.sending) const _TypingIndicator(),
          const Divider(height: 1),
          _buildComposer(chat),
        ],
      ),
    );
  }

  Widget _buildMessages(ChatProvider chat) {
    if (chat.loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (chat.messages.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.health_and_safety_outlined,
                  size: 56, color: Theme.of(context).colorScheme.primary),
              const SizedBox(height: 16),
              Text('Ask a health question',
                  style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              Text(
                'MediAssist provides general information only, '
                'not medical advice.',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        ),
      );
    }
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(12),
      itemCount: chat.messages.length,
      itemBuilder: (_, i) => _MessageBubble(message: chat.messages[i]),
    );
  }

  Widget _buildComposer(ChatProvider chat) {
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 8, 12, 8),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                minLines: 1,
                maxLines: 5,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => _send(),
                decoration: const InputDecoration(
                  hintText: 'Type your question…',
                  border: OutlineInputBorder(),
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                ),
              ),
            ),
            const SizedBox(width: 8),
            IconButton.filled(
              onPressed: chat.sending ? null : _send,
              icon: const Icon(Icons.send),
            ),
          ],
        ),
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  const _MessageBubble({required this.message});

  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final isUser = message.isUser;
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.8,
        ),
        decoration: BoxDecoration(
          color: isUser ? scheme.primary : scheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(16),
        ),
        child: SelectableText(
          message.content,
          style: TextStyle(
            color: isUser ? scheme.onPrimary : scheme.onSurface,
          ),
        ),
      ),
    );
  }
}

class _TypingIndicator extends StatelessWidget {
  const _TypingIndicator();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          SizedBox(
            height: 16,
            width: 16,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
          SizedBox(width: 12),
          Text('MediAssist is thinking…'),
        ],
      ),
    );
  }
}
