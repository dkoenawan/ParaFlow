# Code Architecture: Ports and Adapters

ParaFlow follows the **Ports and Adapters architecture** (also known as Hexagonal Architecture) to maintain clean separation of concerns and enable easy extensibility for different platforms and integrations.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Adapters                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Notion    │  │   Obsidian  │  │   Other     │         │
│  │   Adapter   │  │   Adapter   │  │   Adapters  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                         Ports                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Content    │  │  Webhook    │  │  Storage    │         │
│  │  Port       │  │  Port       │  │  Port       │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Core Domain                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    PARA     │  │ Content     │  │ Organization│         │
│  │ Categorizer │  │ Analyzer    │  │   Engine    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Core Domain

The **Core Domain** contains the business logic and rules that are independent of any external system. This is where the PARA methodology intelligence lives.

### Key Components:

- **PARA Categorizer**: Determines which PARA category (Project, Area, Resource, Archive) content belongs to
- **Content Analyzer**: Analyzes content to extract metadata, identify patterns, and detect changes
- **Organization Engine**: Handles the logic for moving, structuring, and maintaining content organization
- **Domain Models**: Represents core concepts like Projects, Areas, Resources, Archives, and Content

### Domain Services:

- Content classification logic
- PARA transition rules (e.g., when to move a project to archive)
- Organization policies and structure maintenance
- Content relationship management

## Ports

**Ports** define the interfaces that the core domain uses to interact with the outside world. They are contracts that adapters must implement.

### Input Ports (Driving):

- **ContentPort**: Interface for receiving content updates and changes
- **WebhookPort**: Interface for receiving webhook notifications
- **CommandPort**: Interface for manual commands and operations

### Output Ports (Driven):

- **StoragePort**: Interface for persisting and retrieving organized content
- **NotificationPort**: Interface for sending notifications about organization changes
- **ExternalSystemPort**: Interface for interacting with external platforms

## Adapters

**Adapters** implement the ports and handle the technical details of integrating with specific external systems.

### Input Adapters (Primary):

- **HTTP Webhook Adapter**: Receives webhooks from external systems
- **REST API Adapter**: Provides HTTP endpoints for manual operations
- **Scheduler Adapter**: Triggers periodic scanning and organization tasks
- **CLI Adapter**: Command-line interface for direct interaction

### Output Adapters (Secondary):

- **Notion Adapter**: Implements ExternalSystemPort for Notion integration
- **Obsidian Adapter**: Implements ExternalSystemPort for Obsidian integration
- **Database Adapter**: Implements StoragePort for data persistence
- **Email Adapter**: Implements NotificationPort for email notifications

## Benefits of This Architecture

1. **Platform Agnostic**: The core domain doesn't know about Notion, Obsidian, or any specific platform
2. **Testability**: Core business logic can be tested independently of external dependencies
3. **Extensibility**: New platforms can be added by implementing the appropriate adapters
4. **Maintainability**: Changes to external systems only affect their respective adapters
5. **Flexibility**: Different combinations of adapters can be used for different deployment scenarios

## Example Flow

1. **Notion Webhook** → **HTTP Webhook Adapter** → **WebhookPort** → **Core Domain**
2. **Core Domain** processes the content using **PARA Categorizer** and **Organization Engine**
3. **Core Domain** → **StoragePort** → **Database Adapter** (saves state)
4. **Core Domain** → **ExternalSystemPort** → **Notion Adapter** (updates Notion)
5. **Core Domain** → **NotificationPort** → **Email Adapter** (notifies user)

## Directory Structure

```
src/
├── domain/           # Core Domain
│   ├── models/       # Domain entities
│   ├── services/     # Domain services
│   └── ports/        # Port interfaces
├── adapters/         # Adapters implementations
│   ├── input/        # Input adapters
│   └── output/       # Output adapters
└── infrastructure/   # Cross-cutting concerns
```

This architecture ensures that ParaFlow remains flexible, testable, and easily extensible for any platform or integration that contributors want to add.