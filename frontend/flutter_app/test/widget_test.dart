import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:mediassist_app/main.dart';
import 'package:mediassist_app/services/api_client.dart';

void main() {
  testWidgets('shows the login screen when no session is stored',
      (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});

    await tester.pumpWidget(MediAssistApp(apiClient: ApiClient()));
    await tester.pumpAndSettle();

    expect(find.text('MediAssist AI'), findsOneWidget);
    expect(find.text('Sign In'), findsOneWidget);
  });
}
