import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../state/auth_provider.dart';
import '../state/chat_provider.dart';
import 'chat_screen.dart';

class ConversationsScreen extends StatefulWidget {
  const ConversationsScreen({super.key});

  @override
  State<ConversationsScreen> createState() => _ConversationsScreenState();
}

class _ConversationsScreenState extends State<ConversationsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ConversationsProvider>().refresh();
    });
  }

  void _openChat({int? conversationId}) {
    final chat = context.read<ChatProvider>();
    final conversations = context.read<ConversationsProvider>();
    if (conversationId == null) {
      chat.startNew();
    } else {
      chat.openConversation(conversationId);
    }
    Navigator.of(context)
        .push(MaterialPageRoute(builder: (_) => const ChatScreen()))
        .then((_) => conversations.refresh());
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final convos = context.watch<ConversationsProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('MediAssist AI'),
        actions: [
          PopupMenuButton<String>(
            onSelected: (v) {
              if (v == 'logout') auth.logout();
            },
            itemBuilder: (_) => [
              PopupMenuItem(
                enabled: false,
                child: Text(auth.user?.email ?? ''),
              ),
              const PopupMenuItem(value: 'logout', child: Text('Log out')),
            ],
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _openChat(),
        icon: const Icon(Icons.add),
        label: const Text('New chat'),
      ),
      body: RefreshIndicator(
        onRefresh: () => context.read<ConversationsProvider>().refresh(),
        child: _buildBody(convos),
      ),
    );
  }

  Widget _buildBody(ConversationsProvider convos) {
    if (convos.loading && convos.items.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }
    if (convos.error != null && convos.items.isEmpty) {
      return _CenteredMessage(
        icon: Icons.error_outline,
        text: convos.error!,
      );
    }
    if (convos.items.isEmpty) {
      return const _CenteredMessage(
        icon: Icons.chat_bubble_outline,
        text: 'No conversations yet.\nTap "New chat" to begin.',
      );
    }
    return ListView.separated(
      itemCount: convos.items.length,
      separatorBuilder: (_, _) => const Divider(height: 1),
      itemBuilder: (context, i) {
        final c = convos.items[i];
        return Dismissible(
          key: ValueKey(c.id),
          direction: DismissDirection.endToStart,
          background: Container(
            color: Theme.of(context).colorScheme.errorContainer,
            alignment: Alignment.centerRight,
            padding: const EdgeInsets.only(right: 20),
            child: const Icon(Icons.delete_outline),
          ),
          onDismissed: (_) => context.read<ConversationsProvider>().delete(c.id),
          child: ListTile(
            leading: const CircleAvatar(child: Icon(Icons.chat_outlined)),
            title: Text(c.title, maxLines: 1, overflow: TextOverflow.ellipsis),
            subtitle: Text(_formatDate(c.updatedAt)),
            onTap: () => _openChat(conversationId: c.id),
          ),
        );
      },
    );
  }

  String _formatDate(DateTime dt) {
    final local = dt.toLocal();
    String two(int n) => n.toString().padLeft(2, '0');
    return '${local.year}-${two(local.month)}-${two(local.day)} '
        '${two(local.hour)}:${two(local.minute)}';
  }
}

class _CenteredMessage extends StatelessWidget {
  const _CenteredMessage({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        const SizedBox(height: 120),
        Icon(icon, size: 56, color: Theme.of(context).colorScheme.outline),
        const SizedBox(height: 16),
        Text(text, textAlign: TextAlign.center),
      ],
    );
  }
}
