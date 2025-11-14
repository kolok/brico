import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobileapp/l10n/app_localizations.dart';
import 'package:mobileapp/screens/sign_in_screen.dart';
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
      home: SignInScreen(authService: mockAuthService),
      routes: {
        '/home': (_) => const Placeholder(),
        '/signup': (_) => const Placeholder(),
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
    'affiche les validations lorsque les champs sont vides',
    (tester) async {
      await tester.pumpWidget(buildTestableWidget());

      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();

      expect(find.text('Please enter your email'), findsOneWidget);
      expect(find.text('Please enter your password'), findsOneWidget);
      verifyZeroInteractions(mockAuthService);
    },
  );

  testWidgets(
    'appelle signIn et remplace la route lorsque la connexion est un succès',
    (tester) async {
      when(
        () => mockAuthService.signIn(
          email: any(named: 'email'),
          password: any(named: 'password'),
        ),
      ).thenAnswer((_) async => {'key': 'token'});

      await tester.pumpWidget(buildTestableWidget());

      await tester.enterText(
        find.byType(TextFormField).at(0),
        'user@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'password123',
      );

      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();
      await tester.pumpAndSettle();

      verify(
        () => mockAuthService.signIn(
          email: 'user@example.com',
          password: 'password123',  // pragma: allowlist secret
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
    'affiche un SnackBar lorsque le backend ne renvoie pas de clé',
    (tester) async {
      when(
        () => mockAuthService.signIn(
          email: any(named: 'email'),
          password: any(named: 'password'),
        ),
      ).thenAnswer((_) async => <String, dynamic>{});

      await tester.pumpWidget(buildTestableWidget());

      await tester.enterText(
        find.byType(TextFormField).at(0),
        'user@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'password123',
      );

      await tester.tap(find.byType(ElevatedButton));
      await tester.pump(); // Laisse le temps au SnackBar d'apparaître.

      expect(find.text('Sign-in error'), findsOneWidget);
    },
  );
}

