# Architecture Decisions

This document explains the rationale behind ParaFlow's architectural choices and provides context for contributors who want to understand the "why" behind our design decisions.

For implementation details and structure overview, see [Code Architecture](./code_architecture.md).

## Monorepo Pattern: Apps/Packages

### Decision

ParaFlow uses an **Apps/Packages** monorepo structure where:
- `apps/` contains deployable applications (web, api, cli)
- `packages/` contains shared libraries and domain logic
- Each package follows hexagonal architecture principles

### Rationale

We evaluated three main monorepo patterns:

#### 1. Apps/Packages Pattern ✅ **CHOSEN**

**Structure:**
```
├── apps/                 # Deployable applications
├── packages/             # Shared libraries
└── infrastructure/       # Deployment configs
```

**Benefits:**
- Clear separation between applications and shared code
- Independent deployment of each application
- Shared domain logic reduces code duplication
- Works well with existing hexagonal architecture
- Excellent tooling support (Nx, Lerna, Rush)

**Downsides:**
- Dependency management complexity
- Build coordination when shared packages change
- Version synchronization challenges

#### 2. Services Pattern ❌ **REJECTED**

**Structure:**
```
├── services/             # Microservices
├── web/                  # Frontend
└── shared/               # Shared utilities
```

**Why rejected:**
- ParaFlow's core value is in unified PARA methodology logic
- Splitting domain logic across services would break cohesion
- Network overhead between services unnecessary for our use case
- Operational complexity not justified by current requirements

#### 3. Domain-Driven Pattern ❌ **REJECTED**

**Structure:**
```
├── domains/
│   ├── content/
│   │   ├── frontend/
│   │   └── backend/
│   └── organization/
```

**Why rejected:**
- Would require splitting our cohesive PARA domain
- Cross-domain features difficult (most of ParaFlow is cross-cutting)
- Code duplication across similar domain patterns
- Conflicts with hexagonal architecture boundaries

### Apps/Packages + Hexagonal Architecture

Our chosen pattern complements hexagonal architecture perfectly:

- **Domain packages** contain ports and core business logic
- **Adapter packages** implement external integrations
- **App packages** compose domain + adapters for specific use cases
- **Shared packages** provide common types and utilities

This maintains clean dependency direction while enabling code reuse across applications.

## Why Hexagonal Architecture?

### Decision

ParaFlow uses **Hexagonal Architecture** (Ports and Adapters) for internal structure.

### Rationale

We evaluated several architectural patterns:

#### Hexagonal Architecture ✅ **CHOSEN**

**Benefits:**
- **Platform Agnostic**: Core PARA logic independent of Notion, Obsidian, etc.
- **Testability**: Business logic testable without external dependencies
- **Extensibility**: New platforms added via adapters
- **Maintainability**: External changes only affect respective adapters

**Perfect fit for ParaFlow because:**
- Multiple platform integrations (Notion, Obsidian, future platforms)
- Complex domain logic that needs to be platform-independent
- CLI, web, and API all need same core functionality

#### Alternatives Considered

**Layered Architecture**: Too rigid for our multi-platform needs
**MVC**: Domain logic would be scattered across models/controllers
**Feature-Based**: Would duplicate PARA logic across features
**Simple Modular**: Risk of tangled dependencies between modules

### Microservices Compatibility

Hexagonal architecture and microservices are complementary:
- **Hexagonal** = internal structure of each service
- **Microservices** = distribution strategy across services

Each microservice can use hexagonal architecture internally. For ParaFlow, we start with a monolith using hexagonal architecture and can extract services later if needed for scaling specific domains.

## Integration Strategy

### Current State
- Single application with hexagonal architecture
- CLI interface as primary interaction method

### Future State
- Multiple applications sharing core domain logic
- Web interface for visual organization
- API for external integrations
- CLI for power users and automation

### Migration Path
1. Extract current domain logic into packages
2. Create shared types package for API contracts
3. Build web application using domain packages
4. Build API server using same domain packages
5. Refactor CLI to use packaged domain logic

This approach ensures we maintain architectural consistency while scaling to multiple applications.

## Decision Criteria

When evaluating architectural choices, we prioritize:

1. **Domain Cohesion**: PARA methodology should remain unified
2. **Platform Independence**: Support multiple note-taking platforms
3. **Code Reuse**: Minimize duplication across applications
4. **Testability**: Enable comprehensive testing of business logic
5. **Extensibility**: Easy to add new platforms and features
6. **Simplicity**: Avoid over-engineering for current needs

These criteria guided our selection of Apps/Packages + Hexagonal Architecture as the optimal combination for ParaFlow's requirements.