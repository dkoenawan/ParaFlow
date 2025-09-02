"""
ParaFlow Test Suite

Comprehensive test suite following hexagonal architecture testing strategy.
Tests are organized by layer and type to ensure proper separation of concerns
and comprehensive coverage.

Test Structure:
├── unit/           # Fast, isolated unit tests
│   ├── domain/     # Domain layer tests (pure business logic)
│   ├── application/ # Application layer tests (use cases)
│   ├── infrastructure/ # Infrastructure layer tests (with mocks)
│   └── interfaces/ # Interface layer tests (controllers, CLI)
├── integration/    # Integration tests with external systems
│   ├── repositories/ # Database integration tests
│   ├── external/   # External service integration tests
│   └── api/        # API integration tests
├── e2e/           # End-to-end acceptance tests
└── fixtures/      # Test data and fixtures

Testing Principles:
- Unit tests: Fast, isolated, mock external dependencies
- Integration tests: Test adapter implementations with real systems
- E2E tests: Full system tests through external interfaces
- Test pyramid: Many unit tests, fewer integration, few E2E tests
"""

__version__ = "0.1.0"