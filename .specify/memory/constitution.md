<!-- Sync Impact Report
Version change: 1.0.0 → 1.0.1 (patch - version consistency fix)
Modified principles: N/A (no content changes)
Added sections: N/A (patch version)
Removed sections: N/A (patch version)
Templates requiring updates:
  ✅ plan-template.md - Updated constitution version reference from v2.1.1 to v1.0.1
  ✅ spec-template.md - No constitution references, aligned
  ✅ tasks-template.md - No constitution references, aligned
Follow-up TODOs:
  ✅ TODO(RATIFICATION_DATE): Set to 2025-09-21 (initial implementation date)
-->

# ParaFlow Constitution

## Core Principles

### I. Hexagonal Architecture First
Every feature MUST adhere to hexagonal architecture principles with clear separation between domain, application, and infrastructure layers. The domain layer MUST remain technology-agnostic. All external dependencies MUST be accessed through ports (interfaces) with adapters providing concrete implementations. This ensures the business logic remains isolated and testable independent of external systems.

### II. Test-Driven Development (NON-NEGOTIABLE)
TDD is mandatory for all feature development. Tests MUST be written first, get user approval, fail initially, then implementation follows. The Red-Green-Refactor cycle MUST be strictly enforced. Contract tests MUST be created for all API endpoints before implementation. Integration tests MUST validate complete user workflows. Unit tests MUST cover domain logic with at least 80% coverage.

### III. PARA Framework Alignment
All features MUST support the PARA methodology (Projects, Areas, Resources, Archives) for information organization. Every thought or piece of information MUST be categorizable into one of the four PARA categories. The system MUST provide clear workflows for moving items between categories as their actionability changes.

### IV. Clean Code & Documentation
Code MUST follow PEP 8 standards for Python. All public functions and classes MUST have comprehensive docstrings. Type hints are required for all function signatures. README files MUST be maintained for each package. API documentation MUST be auto-generated from code annotations.

### V. Async-First Design
All I/O operations MUST use async/await patterns. Database operations, API calls, and file operations MUST be non-blocking. The system MUST support concurrent request handling. Synchronous operations are only permitted for CPU-bound tasks with explicit justification.

## Technology Standards

### Required Stack
- **Language**: Python 3.11+ exclusively
- **Testing**: pytest for all test suites
- **Async**: asyncio and aiohttp for concurrent operations
- **Type Checking**: mypy with strict mode enabled
- **Documentation**: Sphinx for API docs, Markdown for guides

### Architectural Patterns
- Ports and Adapters pattern for all external integrations
- Repository pattern for data persistence
- Use Case pattern for application logic
- Value Objects and Entities in domain layer
- Dependency injection for loose coupling

## Development Workflow

### Branch Strategy
- Feature branches: `feature/###-description`
- Bugfix branches: `bugfix/###-description`
- All features MUST reference an issue number
- Direct commits to main branch are prohibited

### Review Requirements
- All PRs MUST pass automated tests
- Architecture compliance check required
- At least one approval before merge
- Breaking changes require migration plan

### Quality Gates
- Tests MUST pass (100% of test suite)
- Coverage MUST meet minimum (80% for new code)
- Type checking MUST pass with no errors
- Linting MUST show no violations

## Governance

The Constitution supersedes all other project practices and guidelines. Any deviation from constitutional principles MUST be documented with explicit justification in the Complexity Tracking section of implementation plans.

### Amendment Process
1. Propose changes via GitHub issue with rationale
2. Document impact on existing codebase
3. Create migration plan for affected components
4. Obtain consensus from maintainers
5. Update version following semantic versioning

### Compliance Verification
- All implementation plans MUST include Constitution Check section
- PRs failing constitution compliance are automatically rejected
- Quarterly reviews ensure ongoing alignment
- Violations tracked in project metrics

### Version Policy
- MAJOR: Removal or fundamental change to core principles
- MINOR: Addition of new principles or significant expansions
- PATCH: Clarifications, wording improvements, typo fixes

**Version**: 1.0.1 | **Ratified**: 2025-09-21 | **Last Amended**: 2025-09-24