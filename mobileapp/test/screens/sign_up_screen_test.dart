import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobileapp/l10n/app_localizations.dart';
import 'package:mobileapp/screens/sign_up_screen.dart';
import 'package:mobileapp/services/auth_service.dart';
import 'package:mocktail/mocktail.dart';

class _MockAuthService extends Mock implements AuthService {}

class _MockNavigatorObserver extends Mock implements NavigatorObserver {}

class _FakeRoute extends Fake implements Route<dynamic> {}

void main() {
  late _MockAuthService mockAuthService;
  late _MockNavigatorObserver mockNavigatorObserver;

  Widget buildTestableWidget() {
    return MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: SignUpScreen(authService: mockAuthService),
      routes: {
        '/home': (_) => const Placeholder(),
      },
      navigatorObservers: [mockNavigatorObserver],
    );
  }

  setUpAll(() {
    registerFallbackValue(_FakeRoute());
  });

  setUp(() {
    mockAuthService = _MockAuthService();
    mockNavigatorObserver = _MockNavigatorObserver();
  });

  testWidgets(
    'affiche les erreurs de validation pour des champs manquants',
    (tester) async {
      await tester.pumpWidget(buildTestableWidget());

      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();

      expect(find.text('Please enter your email'), findsOneWidget);
      expect(find.text('Please confirm your email'), findsOneWidget);
      expect(find.text('Please enter your password'), findsOneWidget);
      expect(find.text('Please confirm your password'), findsOneWidget);
      verifyZeroInteractions(mockAuthService);
    },
  );

  testWidgets(
    'indique une erreur lorsque les emails ne correspondent pas',
    (tester) async {
      await tester.pumpWidget(buildTestableWidget());

      await tester.enterText(
        find.byType(TextFormField).at(0),
        'user@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'different@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).at(2),
        'password123',
      );
      await tester.enterText(
        find.byType(TextFormField).at(3),
        'password123',
      );

      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();

      expect(find.text('Email addresses do not match'), findsOneWidget);
      verifyZeroInteractions(mockAuthService);
    },
  );

  testWidgets(
    'navigue vers home lorsque la création de compte réussit',
    (tester) async {
      when(
        () => mockAuthService.signUp(
          email: any(named: 'email'),
          emailConfirmation: any(named: 'emailConfirmation'),
          password1: any(named: 'password1'),
          password2: any(named: 'password2'),
        ),
      ).thenAnswer((_) async => {'key': 'token'});

      await tester.pumpWidget(buildTestableWidget());

      await tester.enterText(
        find.byType(TextFormField).at(0),
        'user@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'user@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).at(2),
        'password123',
      );
      await tester.enterText(
        find.byType(TextFormField).at(3),
        'password123',
      );

      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();
      await tester.pumpAndSettle();

      verify(
        () => mockAuthService.signUp(
          email: 'user@example.com',
          emailConfirmation: 'user@example.com',
          password1: 'password123',  // pragma: allowlist secret
          password2: 'password123',  // pragma: allowlist secret
        ),
      ).called(1);
      verify(
        () => mockNavigatorObserver.didReplace(
          newRoute: any(named: 'newRoute'),
          oldRoute: any(named: 'oldRoute'),
        ),
      ).called(1);
    },
  );

  testWidgets(
    'affiche un message d\'erreur lorsque le backend ne renvoie pas de clé',
    (tester) async {
      when(
        () => mockAuthService.signUp(
          email: any(named: 'email'),
          emailConfirmation: any(named: 'emailConfirmation'),
          password1: any(named: 'password1'),
          password2: any(named: 'password2'),
        ),
      ).thenAnswer((_) async => <String, dynamic>{});

      await tester.pumpWidget(buildTestableWidget());

      await tester.enterText(
        find.byType(TextFormField).at(0),
        'user@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'user@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).at(2),
        'password123',
      );
      await tester.enterText(
        find.byType(TextFormField).at(3),
        'password123',
      );

      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();

      expect(find.text('Sign-up error'), findsOneWidget);
    },
  );

  testWidgets(
    'affiche le message générique lorsque le backend lève une exception',
    (tester) async {
      when(
        () => mockAuthService.signUp(
          email: any(named: 'email'),
          emailConfirmation: any(named: 'emailConfirmation'),
          password1: any(named: 'password1'),
          password2: any(named: 'password2'),
        ),
      ).thenThrow(Exception('Unreachable backend'));

      await tester.pumpWidget(buildTestableWidget());

      await tester.enterText(
        find.byType(TextFormField).at(0),
        'user@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'user@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).at(2),
        'password123',
      );
      await tester.enterText(
        find.byType(TextFormField).at(3),
        'password123',
      );

      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();

      expect(find.textContaining('Error: Exception: Unreachable backend'), findsOneWidget);
    },
  );
}

