import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/dashboard_service.dart';
import '../services/document_service.dart';
import '../services/rag_service.dart';
import 'conversations_screen.dart';
import 'dashboard_screen.dart';
import 'documents_screen.dart';
import 'rag_screen.dart';

/// Authenticated home: bottom-nav shell across Dashboard, Chats,
/// Documents, and Ask (RAG).
class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [
      DashboardScreen(service: context.read<DashboardService>()),
      const ConversationsScreen(),
      DocumentsScreen(service: context.read<DocumentService>()),
      RagScreen(service: context.read<RagService>()),
    ];

    return Scaffold(
      body: IndexedStack(index: _index, children: pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(
              icon: Icon(Icons.dashboard_outlined),
              selectedIcon: Icon(Icons.dashboard),
              label: 'Dashboard'),
          NavigationDestination(
              icon: Icon(Icons.chat_outlined),
              selectedIcon: Icon(Icons.chat),
              label: 'Chats'),
          NavigationDestination(
              icon: Icon(Icons.folder_outlined),
              selectedIcon: Icon(Icons.folder),
              label: 'Documents'),
          NavigationDestination(
              icon: Icon(Icons.search_outlined),
              selectedIcon: Icon(Icons.search),
              label: 'Ask'),
        ],
      ),
    );
  }
}
