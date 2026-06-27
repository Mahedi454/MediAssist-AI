import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../state/auth_provider.dart';

/// AppBar action showing the signed-in email and a logout option.
class LogoutButton extends StatelessWidget {
  const LogoutButton({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    return PopupMenuButton<String>(
      icon: const Icon(Icons.account_circle_outlined),
      onSelected: (v) {
        if (v == 'logout') context.read<AuthProvider>().logout();
      },
      itemBuilder: (_) => [
        PopupMenuItem(enabled: false, child: Text(auth.user?.email ?? '')),
        const PopupMenuItem(value: 'logout', child: Text('Log out')),
      ],
    );
  }
}
