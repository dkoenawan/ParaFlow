# Research: MVP Database CRUD

**Feature**: 001-mvp-database-crud
**Date**: 2025-10-02

## Research Questions & Findings

### 1. Notion Database API Capabilities

**Question**: What are the Notion API endpoints and capabilities for database operations?

**Decision**: Use Notion's database endpoints for full CRUD operations
- `POST /databases` - Create database
- `GET /databases/{database_id}` - Retrieve database
- `PATCH /databases/{database_id}` - Update database
- `POST /databases/{database_id}/query` - Query database pages
- Database archival via PATCH with `archived: true`

**Rationale**:
- Notion provides comprehensive database APIs that mirror page operations
- Database structure includes title, properties schema, and parent (page/workspace)
- Property types supported: title, rich_text, number, select, multi_select, date, checkbox, url, email, phone, files, etc.

**Alternatives Considered**:
- Using page-based operations only → Rejected: Databases provide structured data capabilities beyond simple pages
- Third-party Notion libraries → Rejected: Official notion-client SDK is maintained and reliable

### 2. Database vs Database Page Operations

**Question**: How do database CRUD operations differ from database page CRUD operations?

**Decision**: Implement two distinct entity types with separate operations
- **Database**: Container with schema definition (properties configuration)
- **DatabasePage**: Page that exists within a database with property values conforming to schema

**Rationale**:
- Databases define structure (schema), pages hold data within that structure
- Database operations: Manage schema, title, description, parent
- Database page operations: Manage data entries with typed property values

**Alternatives Considered**:
- Single unified entity → Rejected: Conflates schema definition with data, violates SRP
- Page-only approach → Rejected: Loses type safety and structure validation

### 3. Property Schema Design

**Question**: How should we model Notion's property system in our domain?

**Decision**: Use flexible property system with type-specific value objects
- DatabaseProperty value object for schema definition
- PropertyValue for typed data in database pages
- Support core property types: title, rich_text, select, multi_select, date, checkbox

**Rationale**:
- Notion properties are strongly typed - schema defines available types
- Domain model should enforce type safety at property level
- Extensible design allows adding more property types later

**Alternatives Considered**:
- Dictionary-based properties → Rejected: Loses type safety, harder to validate
- Full property type coverage → Deferred: MVP focuses on common types, can extend later

### 4. Existing Architecture Patterns

**Question**: How does the existing Page MVP structure our implementation?

**Decision**: Mirror existing Page patterns for Database operations
- Domain models: Database and DatabasePage entities (similar to Page)
- Ports: DatabaseRepositoryPort interface
- Adapters: Extend NotionPageRepositoryAdapter or create NotionDatabaseRepositoryAdapter
- Use cases: DatabaseOperations (parallel to PageOperations)

**Rationale**:
- Consistency with existing MVP reduces cognitive load
- Proven hexagonal architecture patterns from Page implementation
- Uses existing async-to-sync wrapper pattern (_run_sync helper)

**Alternatives Considered**:
- Separate adapter class → Selected: Cleaner separation of concerns
- Unified repository → Rejected: Violates single responsibility, harder to test

### 5. Validation Strategy

**Question**: What validation is needed for database operations?

**Decision**: Multi-layer validation approach
- Domain layer: Business rules (title required, property schema validation)
- Application layer: Use case orchestration and workflow validation
- Infrastructure layer: Notion API error handling and mapping

**Rationale**:
- Edge cases defined in spec require user confirmation on destructive operations
- Property type validation prevents invalid data entry
- Schema changes need validation against existing data

**Alternatives Considered**:
- API-level validation only → Rejected: Domain logic should be technology-agnostic
- Pydantic models → Deferred: Current MVP uses dataclasses, maintain consistency

### 6. Error Handling Patterns

**Question**: How should we handle database-specific errors?

**Decision**: Extend existing exception hierarchy
- DatabaseCreationError, DatabaseUpdateError, DatabaseDeletionError, DatabaseRetrievalError
- DatabasePageCreationError, etc. for database page operations
- Map Notion API errors to domain exceptions

**Rationale**:
- Follows existing pattern from Page operations
- Specific exceptions for database vs page errors aid debugging
- Edge cases require user alerts - specific errors enable better UX

**Alternatives Considered**:
- Generic exceptions → Rejected: Harder to provide specific user feedback
- HTTP exceptions directly → Rejected: Violates hexagonal architecture

### 7. Testing Strategy

**Question**: What testing approach ensures quality for database operations?

**Decision**: Three-tier testing strategy
- Contract tests: Validate Notion API request/response formats
- Integration tests: Test complete database workflows (create → update → delete)
- Unit tests: Test domain logic and validation rules

**Rationale**:
- TDD constitutional requirement mandates tests first
- Contract tests catch API changes early
- Integration tests validate user scenarios from spec
- 80% coverage target per constitution

**Alternatives Considered**:
- E2E tests only → Rejected: Too slow for TDD cycle
- Mocking Notion API → Included: For unit tests, but also need real API integration tests

## Technical Decisions Summary

| Area | Decision | Impact |
|------|----------|--------|
| API Client | Use existing notion-client SDK | No new dependencies |
| Architecture | Hexagonal with Database/DatabasePage entities | Extends existing pattern |
| Async Pattern | Sync operations with _run_sync wrapper | Consistent with Page MVP |
| Property System | Typed property values with schema | Type safety in domain |
| Validation | Multi-layer (domain/application/infra) | Robust error handling |
| Testing | Contract + Integration + Unit | Comprehensive coverage |

## Open Questions

None - all technical context clarified.

## References

- [Notion API Documentation - Databases](https://developers.notion.com/reference/database)
- [Notion API Documentation - Pages in Databases](https://developers.notion.com/reference/page)
- Existing implementation: `/packages/infrastructure/adapters/notion_adapter.py`
- Constitution: `/.specify/memory/constitution.md`
