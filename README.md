# ParaFlow

**ParaFlow** is a hexagonal architecture monorepo implementing an AI-powered personal assistant that captures, processes, and organizes your thoughts into the PARA framework (Projects, Areas, Resources, Archives).

## Project Overview

This project follows hexagonal architecture principles (ports and adapters pattern) to ensure clean separation of concerns, testability, and maintainability. The monorepo structure enables modular development while maintaining architectural boundaries.

## Architecture

ParaFlow implements a hexagonal architecture with four distinct layers:

### Package Structure

```
packages/
├── domain/           # Core business logic (entities, value objects, domain services)
│   ├── models/       # Domain models and entities
│   ├── ports/        # Interface definitions (ports)
│   └── services/     # Domain services
├── application/      # Application orchestration layer
│   ├── use_cases/    # Application use cases
│   ├── handlers/     # Command/query handlers
│   └── config/       # Application configuration
├── infrastructure/   # External integrations and technical concerns
│   ├── repositories/ # Data persistence adapters
│   ├── external/     # External service adapters
│   ├── events/       # Event handling infrastructure
│   └── adapters/     # Technical adapters
└── interfaces/       # External interfaces (driving adapters)
    ├── api/          # REST API interface
    ├── cli/          # Command-line interface
    └── webhooks/     # Webhook endpoints
```

### Test Structure

```
tests/
├── unit/            # Fast, isolated unit tests by layer
│   ├── domain/      # Domain layer unit tests
│   ├── application/ # Application layer unit tests
│   ├── infrastructure/ # Infrastructure layer unit tests
│   └── interfaces/  # Interface layer unit tests
├── integration/     # Integration tests for adapters
├── e2e/            # End-to-end acceptance tests
├── fixtures/       # Shared test data and utilities
└── conftest.py     # Global pytest configuration
```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/dkoenawan/ParaFlow.git
cd ParaFlow
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

### Development Tools

The project includes comprehensive development tooling:

- **Testing**: `pytest` with coverage reporting
- **Code Formatting**: `black` for consistent code style
- **Import Sorting**: `isort` for organized imports
- **Type Checking**: `mypy` for static type analysis
- **Linting**: `flake8` for code quality
- **Pre-commit**: Automated code quality checks

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e           # End-to-end tests only

# Run with coverage
pytest --cov=packages --cov-report=html
```

### Code Quality

```bash
# Format code
black packages/ tests/

# Sort imports
isort packages/ tests/

# Type checking
mypy packages/

# Linting
flake8 packages/ tests/
```

## Project Status

- **Phase 0.1**: ✅ Project Structure Setup (Issue #13, PR #32)
  - Complete hexagonal architecture skeleton implemented
  - Package structure with proper imports configured
  - Comprehensive test framework established
  - Development tooling configured

## Contributing

This project follows hexagonal architecture principles. When contributing:

1. Maintain architectural boundaries between layers
2. Use dependency inversion (domain should not depend on infrastructure)
3. Write tests for all layers following the test pyramid
4. Follow the established code style and conventions

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
