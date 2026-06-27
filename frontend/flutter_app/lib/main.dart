import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'services/api_client.dart';
import 'services/auth_service.dart';
import 'services/chat_service.dart';
import 'state/auth_provider.dart';
import 'state/chat_provider.dart';
import 'screens/login_screen.dart';
import 'screens/conversations_screen.dart';

void main() {
  final apiClient = ApiClient();
  runApp(MediAssistApp(apiClient: apiClient));
}

class MediAssistApp extends StatelessWidget {
  const MediAssistApp({super.key, required this.apiClient});

  final ApiClient apiClient;

  @override
  Widget build(BuildContext context) {
    final chatService = ChatService(apiClient);
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => AuthProvider(
            apiClient: apiClient,
            authService: AuthService(apiClient),
          )..loadSession(),
        ),
        ChangeNotifierProvider(create: (_) => ChatProvider(chatService)),
        ChangeNotifierProvider(create: (_) => ConversationsProvider(chatService)),
      ],
      child: MaterialApp(
        title: 'MediAssist AI',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1B998B)),
          useMaterial3: true,
        ),
        home: const _RootGate(),
      ),
    );
  }
}

/// Routes between login and the home screen based on auth status.
class _RootGate extends StatelessWidget {
  const _RootGate();

  @override
  Widget build(BuildContext context) {
    final status = context.watch<AuthProvider>().status;
    switch (status) {
      case AuthStatus.unknown:
        return const Scaffold(
          body: Center(child: CircularProgressIndicator()),
        );
      case AuthStatus.authenticated:
        return const ConversationsScreen();
      case AuthStatus.unauthenticated:
        return const LoginScreen();
    }
  }
}
