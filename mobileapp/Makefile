# Variables
FLUTTER := flutter
FLUTTER_FORMAT := dart format

# Colors for the output
YELLOW := \033[1;33m
GREEN := \033[1;32m
NC := \033[0m # No Color

# Default target
.PHONY: help
help:
	@echo "$(GREEN)Available commands for MobileApp (Flutter):$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup and configuration:$(NC)"
	@echo "  make install           - Install Flutter dependencies"
	@echo "  make upgrade           - Update dependencies"
	@echo "  make upgrade-major     - Update dependencies (major versions)"
	@echo "  make doctor            - Check the Flutter installation"
	@echo "  make devices           - List available devices"
	@echo "  make localizations     - Generate localization files"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  make run               - Launch the app on the default device"
	@echo "  make hot-reload        - Launch with hot reload (debug mode)"
	@echo ""
	@echo "$(YELLOW)Build:$(NC)"
	@echo "  make build-android     - Build the Android APK (release)"
	@echo "  make build-android-apk - Build the Android APK"
	@echo "  make build-android-aab - Build the Android AAB (Play Store)"
	@echo "  make build-ios         - Build for iOS"
	@echo "  make build-web         - Build for the web"
	@echo "  make build-all         - Build for all platforms"
	@echo ""
	@echo "$(YELLOW)Code quality:$(NC)"
	@echo "  make test              - Run all tests"
	@echo "  make test-coverage     - Run tests with coverage"
	@echo "  make analyze           - Analyze the code (lint)"
	@echo "  make format            - Format the code"
	@echo "  make check-format      - Check code formatting"
	@echo "  make lint              - Analyze and check formatting"
	@echo ""
	@echo "$(YELLOW)Cleaning:$(NC)"
	@echo "  make clean             - Clean build files"
	@echo "  make clean-all         - Full cleanup (build + cache)"
	@echo "  make reset             - Full reset and reinstall"
	@echo ""
	@echo "$(YELLOW)Utilities:$(NC)"
	@echo "  make pub-outdated      - Check available updates"
	@echo "  make pub-upgrade-dry   - Simulate an upgrade"

# Installation and configuration
.PHONY: install
install:
	@echo "$(GREEN)Installing Flutter dependencies...$(NC)"
	$(FLUTTER) pub get

.PHONY: upgrade
upgrade:
	@echo "$(GREEN)Updating dependencies...$(NC)"
	$(FLUTTER) pub upgrade

.PHONY: upgrade-major
upgrade-major:
	@echo "$(GREEN)Updating dependencies (major versions)...$(NC)"
	$(FLUTTER) pub upgrade --major-versions

.PHONY: doctor
doctor:
	@echo "$(GREEN)Checking the Flutter installation...$(NC)"
	$(FLUTTER) doctor -v

.PHONY: devices
devices:
	@echo "$(GREEN)Available devices:$(NC)"
	$(FLUTTER) devices

# Development
.PHONY: run
run:
	@echo "$(GREEN)Launching the app...$(NC)"
	$(FLUTTER) run

.PHONY: hot-reload
hot-reload:
	@echo "$(GREEN)Launching with hot reload...$(NC)"
	$(FLUTTER) run --hot

# Build
.PHONY: build-android
build-android: build-android-apk

.PHONY: build-android-apk
build-android-apk:
	@echo "$(GREEN)Building the Android APK...$(NC)"
	$(FLUTTER) build apk --release

.PHONY: build-android-aab
build-android-aab:
	@echo "$(GREEN)Building the Android AAB for the Play Store...$(NC)"
	$(FLUTTER) build appbundle --release

.PHONY: build-ios
build-ios:
	@echo "$(GREEN)Building for iOS...$(NC)"
	$(FLUTTER) build ios --release

.PHONY: build-web
build-web:
	@echo "$(GREEN)Building for the web...$(NC)"
	$(FLUTTER) build web --release

.PHONY: build-all
build-all: build-android-apk build-android-aab build-web
	@echo "$(GREEN)Full build completed!$(NC)"

# Code quality
.PHONY: test
test:
	@echo "$(GREEN)Running tests...$(NC)"
	$(FLUTTER) test

.PHONY: test-coverage
test-coverage:
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	$(FLUTTER) test --coverage
	@echo "$(YELLOW)Coverage report available in coverage/lcov.info$(NC)"

.PHONY: analyze
analyze:
	@echo "$(GREEN)Analyzing the code...$(NC)"
	$(FLUTTER) analyze

.PHONY: format
format:
	@echo "$(GREEN)Formatting the code...$(NC)"
	$(FLUTTER_FORMAT) lib/ test/ -l 120

.PHONY: check-format
check-format:
	@echo "$(GREEN)Checking formatting...$(NC)"
	$(FLUTTER_FORMAT) --set-exit-if-changed lib/ test/ -l 120

.PHONY: lint
lint: analyze check-format
	@echo "$(GREEN)All checks completed!$(NC)"

# Cleaning
.PHONY: clean
clean:
	@echo "$(GREEN)Cleaning build files...$(NC)"
	$(FLUTTER) clean

.PHONY: clean-all
clean-all: clean
	@echo "$(GREEN)Performing full cleanup...$(NC)"
	rm -rf .dart_tool/
	rm -rf build/
	rm -rf .flutter-plugins
	rm -rf .flutter-plugins-dependencies
	rm -rf .packages
	rm -rf pubspec.lock

.PHONY: reset
reset: clean-all
	@echo "$(GREEN)Full reset and reinstallation...$(NC)"
	$(FLUTTER) pub get
	@echo "$(GREEN)Reset completed!$(NC)"

# Utilities
.PHONY: pub-outdated
pub-outdated:
	@echo "$(GREEN)Checking available updates...$(NC)"
	$(FLUTTER) pub outdated

.PHONY: pub-upgrade-dry
pub-upgrade-dry:
	@echo "$(GREEN)Simulating upgrade...$(NC)"
	$(FLUTTER) pub upgrade --dry-run

.PHONY: localizations
localizations:
	@echo "$(GREEN)Generating localization files...$(NC)"
	$(FLUTTER) gen-l10n

# Production build helper
.PHONY: release-info
release-info:
	@echo "$(YELLOW)Information for production builds:$(NC)"
	@echo ""
	@echo "Android APK: build/app/outputs/flutter-apk/app-release.apk"
	@echo "Android AAB: build/app/outputs/bundle/release/app-release.aab"
	@echo "iOS: build/ios/iphoneos/Runner.app"
	@echo "Web: build/web/"
	@echo ""
	@echo "To sign the Android APK, configure android/key.properties"
	@echo "For iOS, configure the provisioning profile in Xcode"

