# MobileApp Agent Notes (Flutter)

## Scope

This file applies to **`mobileapp/` only**. For monorepo overview, see [../CLAUDE.md](../CLAUDE.md).

## Project Structure

```
mobileapp/
├── lib/                           # Dart source code
│   ├── main.dart                  # App entry point
│   ├── l10n/                      # Localization files
│   │   ├── app_en.arb            # English strings
│   │   └── app_fr.arb            # French strings
│   ├── generated/                 # Generated l10n files (do not edit)
│   │   └── l10n.dart
│   ├── screens/                   # Page/screen widgets
│   ├── widgets/                   # Reusable widget components
│   ├── services/                  # Business logic (API, storage, etc.)
│   ├── models/                    # Data models
│   └── utils/                     # Utility functions
├── test/                          # Unit and widget tests
│   ├── widget_test.dart
│   └── unit_test.dart
├── ios/                           # iOS native code
├── android/                       # Android native code
├── web/                           # Web build files
├── l10n.yaml                      # Localization configuration
├── pubspec.yaml                   # Flutter dependencies
├── pubspec.lock                   # Locked dependency versions
├── Makefile                       # Dev commands
└── analysis_options.yaml          # Lint rules
```

**App organization**: Widgets are organized by feature/screen. Keep business logic in `services/` and `models/`, not in widget classes. Prefer immutable, well-structured widgets.

## Default Workflow (Follow This)

1. **Explore**: Locate the widget/page/service involved and read existing tests.
2. **Plan**: Propose the smallest change that keeps UI behavior consistent across platforms.
3. **Implement**:
   - Prefer **immutable widgets** and official Dart conventions.
   - Keep business logic testable (avoid embedding logic deep in widgets).
   - Use `const` constructors where possible.
4. **Verify**:
   - Run unit/widget tests: `make test`
   - Run analyzer: `make analyze`
   - Check formatting: `make check-format`
   - If localization changed, regenerate: `make localizations`

## Code Standards

### Dart Style

- **Naming**: `PascalCase` for classes, `camelCase` for variables/functions, `UPPER_CASE` for constants
- **Line length**: 120 characters (configured in Makefile for `dart format`)
- **Imports**: Organize by category (dart, packages, relative imports)
- **Const constructors**: Use `const` for widgets when all parameters are const
- **Type annotations**: Always include return types and parameter types

Example:

```dart
import 'package:flutter/material.dart';
import 'package:my_app/models/audit.dart';

class AuditListScreen extends StatelessWidget {
  const AuditListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Audits')),
      body: const AuditListView(),
    );
  }
}
```

### Widget Structure

- **Immutable widgets**: All widgets should be immutable (use `const` constructors)
- **Separate concerns**: Keep UI in widgets, logic in services/models
- **Naming**: `XyzScreen` for full pages, `XyzWidget` for components, `XyzState` for stateful logic

Example stateful widget:

```dart
class CounterWidget extends StatefulWidget {
  const CounterWidget({super.key});

  @override
  State<CounterWidget> createState() => _CounterWidgetState();
}

class _CounterWidgetState extends State<CounterWidget> {
  int _counter = 0;

  void _increment() {
    setState(() => _counter++);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Count: $_counter'),
        ElevatedButton(onPressed: _increment, child: const Text('Increment')),
      ],
    );
  }
}
```

### Language

- All code and documentation is in **English**

## Commands (Use Make Targets First)

All commands run from the `mobileapp/` directory. Use `make help` to see all targets.

### Setup & Dependencies

```bash
make install              # Install Flutter dependencies (flutter pub get)
make upgrade              # Update dependencies (minor/patch versions)
make upgrade-major        # Update dependencies including major versions
make doctor               # Check Flutter installation
make devices              # List available devices/emulators
```

### Running the App

```bash
make run                  # Launch app on default device
make hot-reload           # Run with hot reload enabled (debug mode)
```

**Development flow**:

1. Run `make run` to start the app
2. Edit code in your editor
3. Press `r` in the terminal to hot-reload
4. Press `R` to hot-restart
5. Press `q` to quit

### Testing

```bash
make test                 # Run all unit and widget tests
make test-coverage        # Run tests with coverage report
```

**Running specific tests**:

```bash
flutter test test/widget_test.dart
flutter test test/services/audit_service_test.dart -v
flutter test --tags smoke  # Run tests tagged as 'smoke'
```

**Test structure**:

- Tests in `test/` directory
- Use `testWidgets()` for widget tests, `test()` for unit tests
- Use descriptive test names
- Mock external services with `mockito` or `mocktail`

Example test:

```dart
void main() {
  group('AuditService', () {
    test('calculateScore returns correct value', () {
      final service = AuditService();
      final score = service.calculateScore(50, 100);
      expect(score, 50.0);
    });

    testWidgets('AuditListScreen displays items', (WidgetTester tester) async {
      await tester.pumpWidget(const MyApp());
      expect(find.byType(ListTile), findsWidgets);
    });
  });
}
```

### Code Quality & Linting

```bash
make analyze              # Run Dart analyzer (linting)
make format               # Format code with dart format (line length 120)
make check-format         # Check formatting without modifying
make lint                 # Run analyzer + check-format (comprehensive)
```

**Before committing**:

1. `make format` – auto-fixes formatting
2. `make analyze` – check for issues (fix manually if needed)
3. `make test` – ensure tests pass
4. Review changes and commit

### Localization

```bash
make localizations        # Run flutter gen-l10n (required after editing ARB files)
```

**Workflow**:

1. Edit `lib/l10n/app_en.arb` (English) or `lib/l10n/app_fr.arb` (French)
2. Add/modify strings: `"key": "English text",`
3. Run `make localizations` to generate Dart code
4. Use in code: `AppLocalizations.of(context)!.key`

**ARB file format**:

```json
{
  "helloWorld": "Hello, World!",
  "greeting": "Hello, {name}!",
  "@greeting": {
    "placeholders": {
      "name": {
        "type": "String"
      }
    }
  }
}
```

Use in widget:

```dart
Text(AppLocalizations.of(context)!.helloWorld)
```

### Building

```bash
make build-android-apk  # Build Android APK (testing)
make build-android-aab  # Build Android AAB (Google Play Store)
make build-ios          # Build iOS (requires Xcode)
make build-web          # Build web version
make build-all          # Build all platforms
```

**Android signing** (for AAB/APK):

- Configure keystore in `android/key.properties`
- Set signing config in `android/app/build.gradle`
- Run `make build-android-aab` for release

**iOS signing** (for App Store):

- Configure provisioning profiles in Xcode
- Set up code signing in `ios/Runner.xcodeproj`
- Use Xcode for final release build

### Cleanup

```bash
make clean               # Clean build artifacts
make clean-all           # Clean + remove cache
make reset               # Full reset and reinstall
```

## Architecture & Patterns

### App Structure

- **Screens**: Full-page widgets in `lib/screens/`, one per file
- **Widgets**: Reusable UI components in `lib/widgets/`
- **Services**: Business logic (API calls, local storage, etc.) in `lib/services/`
- **Models**: Data classes in `lib/models/`, preferably with `freezed` or `equatable` for immutability
- **Utils**: Helper functions in `lib/utils/`

### State Management

Choose based on app complexity:

- **setState**: Simple widget-local state
- **Provider**: Recommended for medium complexity
- **Riverpod**: Type-safe alternative to Provider
- **GetX**: Full solution with routing and state

Example with Provider:

```dart
class AuditProvider extends ChangeNotifier {
  List<Audit> _audits = [];

  List<Audit> get audits => _audits;

  Future<void> loadAudits() async {
    _audits = await AuditService().getAudits();
    notifyListeners();
  }
}

// In widget:
Consumer<AuditProvider>(
  builder: (context, provider, child) {
    return ListView.builder(
      itemCount: provider.audits.length,
      itemBuilder: (context, index) => AuditTile(provider.audits[index]),
    );
  },
)
```

### Service Pattern

Keep API and local storage logic in services:

```dart
class AuditService {
  static const _apiUrl = 'https://api.example.com';

  Future<List<Audit>> getAudits() async {
    final response = await http.get(Uri.parse('$_apiUrl/audits'));
    if (response.statusCode == 200) {
      return (jsonDecode(response.body) as List)
          .map((data) => Audit.fromJson(data))
          .toList();
    }
    throw Exception('Failed to load audits');
  }
}
```

### Data Models

Use immutable models with `==` and `hashCode`:

```dart
import 'package:equatable/equatable.dart';

class Audit extends Equatable {
  final int id;
  final String name;
  final String description;

  const Audit({
    required this.id,
    required this.name,
    required this.description,
  });

  @override
  List<Object?> get props => [id, name, description];

  // Optional: JSON serialization
  factory Audit.fromJson(Map<String, dynamic> json) => Audit(
    id: json['id'],
    name: json['name'],
    description: json['description'],
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'description': description,
  };
}
```

## Internationalization (i18n)

### Supported Languages

- **English** (default)
- **French**

### Adding Translations

1. Edit `lib/l10n/app_en.arb` and `lib/l10n/app_fr.arb`
2. Add/update keys: `"key": "text"`
3. Run `make localizations`
4. Use in code: `AppLocalizations.of(context)!.key`

### ARB File Structure

```json
{
  "title": "My App",
  "greeting": "Hello, {name}!",
  "@greeting": {
    "placeholders": {
      "name": { "type": "String" }
    }
  },
  "itemCount": "{count, plural, =0{No items} =1{One item} other{{count} items}}",
  "@itemCount": {
    "placeholders": {
      "count": { "type": "int" }
    }
  }
}
```

### Important Rules

- **Stable keys**: Avoid renaming keys; deprecate old ones if needed
- **Consistency**: Keep English and French keys synchronized
- **Regenerate always**: After editing ARB files, run `make localizations`
- **No missing keys**: Ensure both `app_en.arb` and `app_fr.arb` have identical keys

## Code Quality Rules

### Testing

- Write tests for **non-trivial logic**
- Write **widget tests** for visual regressions
- **Mock external services** (HTTP, storage)
- Use descriptive test names: `test_<feature>_<scenario>`
- Aim for **>70% coverage** for critical paths

### Logging & Debugging

- Avoid `print()` in production code
- Use `debugPrint()` for debug-only output behind a flag:
  ```dart
  const bool kDebugMode = true;
  if (kDebugMode) debugPrint('Debug: $message');
  ```
- Use Flutter DevTools for performance profiling

### Performance

- Use `const` widgets and constructors
- Use `ListView.builder()` instead of `ListView()` for large lists
- Implement `shouldRebuild()` in `InheritedWidget` to avoid unnecessary rebuilds
- Profile with DevTools (Cmd+Shift+P in VS Code, select "Open DevTools")

## Repo Hygiene

### Never Commit

- **Generated files**: `lib/generated/` or `lib/l10n/generated_localization.dart`
- **Platform-specific builds**: `build/`, `.dart_tool/`, `android/.gradle/`
- **IDE artifacts**: `.vscode/`, `.idea/`, `*.iml`
- **Secrets**: API keys, credentials in code
- **Build artifacts**: `.apk`, `.ipa`, `.aab` files

### Before Committing

- Run `make test` – ensure all tests pass
- Run `make format` – auto-fix formatting
- Run `make analyze` – check for linting issues
- Run `make localizations` if ARB files changed
- Review diffs carefully

### Commit Message Conventions

- Concise and descriptive (e.g., "Add audit detail screen" or "Fix French translations")
- Reference issue if applicable
- Follow project conventions from recent commits

## Troubleshooting

### Common Issues

**Analyzer errors after adding packages**:

- Run `make install` or `flutter pub get`
- Run `make analyze` to verify

**Tests fail with "cannot find test"**:

- Check file paths in test imports
- Run `make localizations` first (generated code needed)
- Run `make analyze` for other issues

**Build fails on Android**:

- Run `make clean`
- Ensure Android SDK is up to date
- Check `local.properties` has SDK path

**Build fails on iOS**:

- Run `make clean`
- Run `cd ios && pod install && cd ..`
- Ensure Xcode is up to date

**Localization not updating**:

- Run `make localizations` after editing ARB files
- Check for syntax errors in JSON (use json linter)
- Verify both `app_en.arb` and `app_fr.arb` exist

**Hot reload not working**:

- Check for syntax errors (analyzer should catch)
- Stop and restart with `make run`
- Check if state is being preserved (hot reload limitation)

## Performance Considerations

- Use `select()` in providers to listen to specific properties only
- Use `ListView.builder()` for large, dynamic lists
- Avoid rebuilding entire subtrees; use `RepaintBoundary` for expensive widgets
- Profile memory usage with DevTools Memory tab
- Use `--split-debug-info` for smaller release APKs
