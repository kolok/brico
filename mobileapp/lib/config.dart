import 'dart:io';

class Config {
  // Configuration for API base URL
  // Default to localhost for development
  // You can override this with environment variables or runtime configuration
  static String get apiBaseUrl {
    // For Android emulator
    if (Platform.isAndroid) {
      return const String.fromEnvironment(
        'API_BASE_URL',
        defaultValue: 'http://10.0.2.2:8000',
      );
    }
    // For iOS simulator
    else if (Platform.isIOS) {
      return const String.fromEnvironment(
        'API_BASE_URL',
        defaultValue: 'http://localhost:8000',
      );
    }
    // For other platforms or production
    else {
      return const String.fromEnvironment(
        'API_BASE_URL',
        defaultValue: 'http://localhost:8000',
      );
    }
  }
}
