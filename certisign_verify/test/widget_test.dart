// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:docuthantic/main.dart';

void main() {
  testWidgets('Vérification de l\'application Doc@uthANTIC', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const DocuthAnticApp());

    // Vérifier que l'application se lance correctement
    // Ce test de base vérifie simplement que l'application peut être initialisée
    // Des tests plus spécifiques pourraient être ajoutés pour vérifier les fonctionnalités
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
