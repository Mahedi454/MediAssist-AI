import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/document.dart';
import '../services/document_service.dart';
import '../state/documents_provider.dart';
import '../widgets/logout_button.dart';
import 'document_detail_screen.dart';

class DocumentsScreen extends StatefulWidget {
  const DocumentsScreen({super.key, required this.service});

  final DocumentService service;

  @override
  State<DocumentsScreen> createState() => _DocumentsScreenState();
}

class _DocumentsScreenState extends State<DocumentsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<DocumentsProvider>().refresh();
    });
  }

  Future<void> _pickAndUpload() async {
    final result = await FilePicker.pickFiles(
      withData: true,
      type: FileType.custom,
      allowedExtensions: const ['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'],
    );
    if (result == null || result.files.isEmpty) return;
    final file = result.files.first;
    final bytes = file.bytes;
    if (bytes == null) return;
    if (!mounted) return;

    final provider = context.read<DocumentsProvider>();
    final messenger = ScaffoldMessenger.of(context);
    final ok = await provider.upload(filename: file.name, bytes: bytes);
    messenger.showSnackBar(SnackBar(
      content: Text(ok ? 'Uploaded ${file.name}' : (provider.error ?? 'Upload failed')),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final docs = context.watch<DocumentsProvider>();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Documents'),
        actions: const [LogoutButton()],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: docs.uploading ? null : _pickAndUpload,
        icon: docs.uploading
            ? const SizedBox(
                height: 18,
                width: 18,
                child: CircularProgressIndicator(strokeWidth: 2))
            : const Icon(Icons.upload_file),
        label: Text(docs.uploading ? 'Uploading…' : 'Upload'),
      ),
      body: RefreshIndicator(
        onRefresh: () => context.read<DocumentsProvider>().refresh(),
        child: _buildBody(docs),
      ),
    );
  }

  Widget _buildBody(DocumentsProvider docs) {
    if (docs.loading && docs.items.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }
    if (docs.items.isEmpty) {
      return ListView(children: const [
        SizedBox(height: 140),
        Icon(Icons.folder_open_outlined, size: 56),
        SizedBox(height: 12),
        Center(child: Text('No documents yet.\nUpload a PDF, DOCX, image, or TXT.',
            textAlign: TextAlign.center)),
      ]);
    }
    return ListView.separated(
      itemCount: docs.items.length,
      separatorBuilder: (_, _) => const Divider(height: 1),
      itemBuilder: (context, i) {
        final d = docs.items[i];
        return Dismissible(
          key: ValueKey(d.id),
          direction: DismissDirection.endToStart,
          background: Container(
            color: Theme.of(context).colorScheme.errorContainer,
            alignment: Alignment.centerRight,
            padding: const EdgeInsets.only(right: 20),
            child: const Icon(Icons.delete_outline),
          ),
          onDismissed: (_) => context.read<DocumentsProvider>().delete(d.id),
          child: ListTile(
            leading: _StatusIcon(status: d.status),
            title: Text(d.originalFilename,
                maxLines: 1, overflow: TextOverflow.ellipsis),
            subtitle: Text(
                '${d.status.name} · ${_formatSize(d.sizeBytes)}'
                '${d.chunkCount != null ? ' · ${d.chunkCount} chunks' : ''}'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Navigator.of(context).push(MaterialPageRoute(
              builder: (_) =>
                  DocumentDetailScreen(documentId: d.id, service: widget.service),
            )),
          ),
        );
      },
    );
  }

  String _formatSize(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }
}

class _StatusIcon extends StatelessWidget {
  const _StatusIcon({required this.status});
  final DocumentStatus status;

  @override
  Widget build(BuildContext context) {
    switch (status) {
      case DocumentStatus.processed:
        return const Icon(Icons.check_circle, color: Colors.green);
      case DocumentStatus.failed:
        return Icon(Icons.error, color: Theme.of(context).colorScheme.error);
      case DocumentStatus.processing:
      case DocumentStatus.pending:
        return const SizedBox(
          height: 24,
          width: 24,
          child: Padding(
            padding: EdgeInsets.all(4),
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
        );
      case DocumentStatus.unknown:
        return const Icon(Icons.insert_drive_file_outlined);
    }
  }
}
