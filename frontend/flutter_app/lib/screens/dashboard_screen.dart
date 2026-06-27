import 'package:flutter/material.dart';

import '../models/dashboard.dart';
import '../services/dashboard_service.dart';
import '../widgets/logout_button.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key, required this.service});

  final DashboardService service;

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  late Future<Dashboard> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.service.get();
  }

  Future<void> _reload() async {
    setState(() => _future = widget.service.get());
    await _future;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: const [LogoutButton()],
      ),
      body: RefreshIndicator(
        onRefresh: _reload,
        child: _buildFuture(context),
      ),
    );
  }

  Widget _buildFuture(BuildContext context) {
    return FutureBuilder<Dashboard>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return ListView(children: [
              const SizedBox(height: 120),
              Center(child: Text('${snapshot.error}')),
            ]);
          }
          final data = snapshot.data!;
          final stats = data.statistics;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text('Overview',
                  style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 12),
              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 1.6,
                children: [
                  _StatCard(
                      label: 'Conversations',
                      value: stats.totalConversations,
                      icon: Icons.chat_outlined),
                  _StatCard(
                      label: 'Messages',
                      value: stats.totalMessages,
                      icon: Icons.message_outlined),
                  _StatCard(
                      label: 'Documents',
                      value: stats.totalDocuments,
                      icon: Icons.description_outlined),
                  _StatCard(
                      label: 'Processed',
                      value: stats.processedDocuments,
                      icon: Icons.task_alt_outlined),
                ],
              ),
              const SizedBox(height: 24),
              if (data.recentUploads.isNotEmpty) ...[
                Text('Recent uploads',
                    style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                ...data.recentUploads.map((d) => ListTile(
                      dense: true,
                      leading: const Icon(Icons.insert_drive_file_outlined),
                      title: Text(d.originalFilename,
                          maxLines: 1, overflow: TextOverflow.ellipsis),
                      subtitle: Text(d.status.name),
                    )),
                const SizedBox(height: 16),
              ],
              if (data.recentChats.isNotEmpty) ...[
                Text('Recent chats',
                    style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                ...data.recentChats.map((c) => ListTile(
                      dense: true,
                      leading: const Icon(Icons.chat_bubble_outline),
                      title: Text(c.title,
                          maxLines: 1, overflow: TextOverflow.ellipsis),
                    )),
              ],
            ],
          );
        },
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard(
      {required this.label, required this.value, required this.icon});

  final String label;
  final int value;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      color: scheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Icon(icon, color: scheme.onPrimaryContainer),
            Text('$value',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    color: scheme.onPrimaryContainer,
                    fontWeight: FontWeight.bold)),
            Text(label, style: TextStyle(color: scheme.onPrimaryContainer)),
          ],
        ),
      ),
    );
  }
}
