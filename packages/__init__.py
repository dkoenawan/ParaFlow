"""
ParaFlow Packages

Monorepo package structure following hexagonal architecture principles.
This module provides the main entry points for all ParaFlow packages.

Architecture Overview:
- domain: Core business logic and domain models (inner layer)
- application: Use cases and application services (application layer)
- infrastructure: External integrations and persistence (outer layer)
- interfaces: API endpoints, CLI, webhooks (outer layer)

Package Structure:
├── domain/          # Domain layer (business logic)
│   ├── models/      # Domain entities and value objects
│   ├── services/    # Domain services
│   └── ports/       # Port interfaces
├── application/     # Application layer
│   ├── use_cases/   # Application use cases
│   ├── handlers/    # Event and command handlers
│   └── config/      # Configuration and DI
├── infrastructure/ # Infrastructure layer
│   ├── repositories/ # Data access implementations
│   ├── external/    # External service integrations
│   ├── events/      # Event infrastructure
│   └── adapters/    # Secondary adapters
└── interfaces/     # Interface layer
    ├── api/        # REST API interfaces
    ├── webhooks/   # Webhook handlers
    └── cli/        # Command-line interfaces
"""

__version__ = "0.1.0"
__all__ = ["domain", "application", "infrastructure", "interfaces"]