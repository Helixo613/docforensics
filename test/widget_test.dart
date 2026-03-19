import 'package:flutter_test/flutter_test.dart';

import 'package:consensus_brief/main.dart';

void main() {
  testWidgets('landing screen renders core DocForensics UI',
      (WidgetTester tester) async {
    await tester.pumpWidget(const ConsensusBriefApp());

    expect(find.text('DocForensics AI'), findsOneWidget);
    expect(find.text('Analyze Documents'), findsOneWidget);
    expect(find.text('Try Demo Data'), findsOneWidget);
  });
}
