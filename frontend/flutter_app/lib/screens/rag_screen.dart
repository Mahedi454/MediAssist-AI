import 'package:flutter/material.dart';

import '../models/rag.dart';
import '../services/rag_service.dart';
import '../widgets/logout_button.dart';

class RagScreen extends StatefulWidget {
  const RagScreen({super.key, required this.service});

  final RagService service;

  @override
  State<RagScreen> createState() => _RagScreenState();
}

class _RagScreenState extends State<RagScreen> {
  final _controller = TextEditingController();
  RagAnswer? _answer;
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _ask() async {
    final question = _controller.text.trim();
    if (question.isEmpty || _loading) return;
    setState(() {
      _loading = true;
      _error = null;
      _answer = null;
    });
    try {
      final answer = await widget.service.ask(question);
      if (mounted) setState(() => _answer = answer);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ask'),
        actions: const [LogoutButton()],
      ),
      body: ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('Ask your documents',
            style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 4),
        Text(
          'Questions are answered using the content of your uploaded documents.',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _controller,
          minLines: 1,
          maxLines: 4,
          textInputAction: TextInputAction.send,
          onSubmitted: (_) => _ask(),
          decoration: const InputDecoration(
            labelText: 'Your question',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 12),
        FilledButton.icon(
          onPressed: _loading ? null : _ask,
          icon: _loading
              ? const SizedBox(
                  height: 18,
                  width: 18,
                  child: CircularProgressIndicator(strokeWidth: 2))
              : const Icon(Icons.search),
          label: Text(_loading ? 'Searching…' : 'Ask'),
        ),
        if (_error != null) ...[
          const SizedBox(height: 16),
          Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
        ],
        if (_answer != null) ...[
          const SizedBox(height: 24),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: SelectableText(_answer!.answer),
            ),
          ),
          if (_answer!.sources.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text('Sources', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            ..._answer!.sources.map((s) => Card(
                  child: ListTile(
                    leading: const Icon(Icons.description_outlined),
                    title: Text('Document ${s.documentId} · chunk ${s.chunkIndex}'),
                    subtitle: Text(s.snippet,
                        maxLines: 3, overflow: TextOverflow.ellipsis),
                  ),
                )),
          ],
        ],
      ],
      ),
    );
  }
}
