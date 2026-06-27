import 'package:flutter/material.dart';

import '../models/document.dart';
import '../services/document_service.dart';

class DocumentDetailScreen extends StatefulWidget {
  const DocumentDetailScreen({
    super.key,
    required this.documentId,
    required this.service,
  });

  final int documentId;
  final DocumentService service;

  @override
  State<DocumentDetailScreen> createState() => _DocumentDetailScreenState();
}

class _DocumentDetailScreenState extends State<DocumentDetailScreen> {
  DocumentDetail? _doc;
  bool _loading = true;
  bool _analyzing = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final doc = await widget.service.get(widget.documentId);
      if (mounted) setState(() => _doc = doc);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _analyze() async {
    setState(() {
      _analyzing = true;
      _error = null;
    });
    try {
      final doc = await widget.service.analyze(widget.documentId);
      if (mounted) setState(() => _doc = doc);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _analyzing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final doc = _doc;
    return Scaffold(
      appBar: AppBar(
        title: Text(doc?.originalFilename ?? 'Document'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : doc == null
              ? Center(child: Text(_error ?? 'Failed to load'))
              : _buildContent(doc),
    );
  }

  Widget _buildContent(DocumentDetail doc) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            Chip(label: Text(doc.status.name)),
            if (doc.chunkCount != null) Chip(label: Text('${doc.chunkCount} chunks')),
            Chip(label: Text(doc.fileExtension.toUpperCase())),
          ],
        ),
        if (_error != null) ...[
          const SizedBox(height: 12),
          Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
        ],
        const SizedBox(height: 16),
        FilledButton.icon(
          onPressed: _analyzing ? null : _analyze,
          icon: _analyzing
              ? const SizedBox(
                  height: 18,
                  width: 18,
                  child: CircularProgressIndicator(strokeWidth: 2))
              : const Icon(Icons.auto_awesome),
          label: Text(_analyzing
              ? 'Analyzing…'
              : (doc.analysis == null ? 'Analyze report' : 'Re-analyze')),
        ),
        if (doc.analysis != null) ...[
          const SizedBox(height: 24),
          Text('Patient-friendly analysis',
              style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: SelectableText(doc.analysis!),
            ),
          ),
        ],
        if (doc.extractedText != null && doc.extractedText!.isNotEmpty) ...[
          const SizedBox(height: 24),
          Text('Extracted text',
              style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: SelectableText(
                doc.extractedText!,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ),
          ),
        ],
      ],
    );
  }
}
