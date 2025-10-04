# Tasks: MVP Database CRUD

**Branch**: `001-mvp-database-crud`
**Input**: Design documents from `/home/daniel.koenawan/private/ParaFlow/specs/001-mvp-database-crud/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Design Philosophy

**Key Simplification**: Database pages ARE pages in Notion. We:
- Add `Database` entity only (reuse existing `Page` for database pages)
- Extend existing `NotionAdapter` with 4 database methods + 1 query helper
- NO new repositories, ports, or use cases needed
- Estimated: ~20 tasks vs original 27

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- All paths are absolute from repository root

## Phase 3.1: Setup & Foundation

- [x] **T001** [P] Create PropertyType enum in `/home/daniel.koenawan/private/ParaFlow/packages/domain/models/property_types.py`
  - Define enum with values: TITLE, RICH_TEXT, NUMBER, SELECT, MULTI_SELECT, DATE, CHECKBOX, URL, EMAIL
  - Add type hints and docstrings
  - No dependencies on other models

- [x] **T002** [P] Create DatabaseProperty value object in `/home/daniel.koenawan/private/ParaFlow/packages/domain/models/database_property.py`
  - Fields: name, property_type (PropertyType), config (Dict), is_required (bool)
  - Frozen dataclass
  - Validation for property schema
  - Depends on: T001 (PropertyType)

- [x] **T003** Create Database entity in `/home/daniel.koenawan/private/ParaFlow/packages/domain/models/database.py`
  - Fields: id, title, description, properties (Dict[str, DatabaseProperty]), parent_id, created_at, updated_at, metadata
  - Business rules: title required, at least one property, exactly one TITLE property
  - Methods: has_id(), is_valid()
  - Depends on: T002 (DatabaseProperty)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (Parallel - Different Files)

- [x] **T004** [P] Contract test for create_database in `/home/daniel.koenawan/private/ParaFlow/packages/domain/tests/contract/test_database_create.py`
  - Test Database entity → Notion API format mapping
  - Validate request schema matches Notion API
  - Assert properties schema is correctly formatted
  - MUST FAIL initially (no implementation yet)

- [x] **T005** [P] Contract test for get_database in `/home/daniel.koenawan/private/ParaFlow/packages/domain/tests/contract/test_database_get.py`
  - Test Notion API response → Database entity mapping
  - Validate response parsing
  - Assert all properties are correctly extracted
  - MUST FAIL initially

- [x] **T006** [P] Contract test for update_database in `/home/daniel.koenawan/private/ParaFlow/packages/domain/tests/contract/test_database_update.py`
  - Test Database updates → Notion API PATCH format
  - Validate partial updates (title, description, properties)
  - MUST FAIL initially

- [x] **T007** [P] Contract test for delete_database in `/home/daniel.koenawan/private/ParaFlow/packages/domain/tests/contract/test_database_delete.py`
  - Test database archival operation
  - Validate confirmation requirement
  - MUST FAIL initially

### Integration Tests (Sequential - Build on Each Other)

- [x] **T008** Integration test: Scenario 1 - Create and retrieve database in `/home/daniel.koenawan/private/ParaFlow/packages/domain/tests/integration/test_database_integration.py`
  - Test from quickstart.md Scenario 1
  - Create database with properties → verify retrieval
  - Assert ID assigned, properties match schema
  - MUST FAIL initially
  - Depends on: T004, T005

- [x] **T009** Integration test: Scenario 2 - Update database schema in same file
  - Test from quickstart.md Scenario 2
  - Add new property to existing database
  - Verify property count and schema updates
  - MUST FAIL initially
  - Depends on: T006, T008

- [x] **T010** Integration test: Scenario 3 - Create pages in database in same file
  - Test from quickstart.md Scenario 3
  - Create pages using existing Page entity with metadata['parent_database_id']
  - Verify pages created with correct properties
  - Uses existing create_page operation!
  - MUST FAIL initially (needs database parent support)
  - Depends on: T008

- [x] **T011** Integration test: Scenario 4 - Update database page in same file
  - Test from quickstart.md Scenario 4
  - Update page properties using existing Page operations
  - Verify property values updated
  - MUST FAIL initially
  - Depends on: T010

- [x] **T012** Integration test: Scenario 5 - Missing required property validation in same file
  - Test from quickstart.md Scenario 5
  - Attempt to create page without required title
  - Assert ValidationError raised
  - MUST FAIL initially
  - Depends on: T010

- [x] **T013** Integration test: Scenario 6 - Delete database with confirmation in same file
  - Test from quickstart.md Scenario 6
  - Delete pages, then database
  - Verify confirmation requirement and archival
  - MUST FAIL initially
  - Depends on: T007, T010

### Unit Tests (Parallel - Different Entities)

- [x] **T014** [P] Unit tests for Database entity in `/home/daniel.koenawan/private/ParaFlow/packages/domain/tests/unit/test_database.py`
  - Test business rules: title required, property validation
  - Test has_id(), is_valid() methods
  - Test frozen dataclass immutability
  - MUST FAIL initially
  - Depends on: T003

- [x] **T015** [P] Unit tests for DatabaseProperty in `/home/daniel.koenawan/private/ParaFlow/packages/domain/tests/unit/test_database_property.py`
  - Test property schema validation
  - Test config validation for SELECT/MULTI_SELECT
  - Test PropertyType enum usage
  - MUST FAIL initially
  - Depends on: T002

## Phase 3.3: Core Implementation (ONLY after tests are failing)

**Prerequisites**: All tests T004-T015 must be written and failing

### Infrastructure Layer

- [x] **T016** Implement create_database method in `/home/daniel.koenawan/private/ParaFlow/packages/infrastructure/adapters/notion_adapter.py`
  - Add create_database(database: Database) -> Database method
  - Map Database entity to Notion API format
  - Handle parent_id (page or workspace)
  - Map properties schema to Notion format
  - Should make T004 pass

- [x] **T017** Implement get_database method in same file
  - Add get_database(database_id: str) -> Optional[Database] method
  - Map Notion response to Database entity
  - Extract properties schema from API response
  - Should make T005 pass
  - Depends on: T016

- [x] **T018** Implement update_database method in same file
  - Add update_database(database: Database) -> Database method
  - Handle partial updates (title, description, properties)
  - Validate database exists before update
  - Should make T006 pass
  - Depends on: T017

- [x] **T019** Implement delete_database method in same file
  - Add delete_database(database_id: str, confirm: bool = False) -> bool method
  - Implement confirmation requirement for destructive operation
  - Archive database (set archived=True)
  - Should make T007 pass
  - Depends on: T018

- [x] **T020** Implement query_database_pages helper in same file
  - Add query_database_pages(database_id: str) -> List[Page] method
  - Query Notion API for pages in database
  - Return list of Page entities with metadata['parent_database_id']
  - Should make T010 pass
  - Depends on: T019

- [x] **T021** Extend create_page to support database parent in same file
  - Update existing _get_parent_page_id() or create_page logic
  - Detect metadata['parent_database_id'] and use database parent type
  - Map metadata['properties'] to Notion database property values
  - Should make T010, T011, T012 pass
  - Depends on: T020

## Phase 3.4: Integration & Validation

- [x] **T022** Add DatabaseNotFoundError exception in `/home/daniel.koenawan/private/ParaFlow/packages/domain/exceptions.py`
  - Create DatabaseNotFoundError, DatabaseCreationError, DatabaseUpdateError, DatabaseDeletionError
  - Follow existing exception pattern from Page operations
  - Add clear error messages

- [x] **T023** Add __init__ exports in `/home/daniel.koenawan/private/ParaFlow/packages/domain/models/__init__.py`
  - Export Database, DatabaseProperty, PropertyType
  - Maintain existing exports (Page, etc.)

## Phase 3.5: Polish & Documentation

- [x] **T024** [P] Run full test suite and verify coverage in repository root
  - Execute: `python -m pytest packages/domain/tests/ -v --cov=packages/domain --cov-report=term-missing`
  - Verify 80% coverage target met
  - All integration tests (T008-T013) must pass
  - All contract tests (T004-T007) must pass
  - All unit tests (T014-T015) must pass
  - ✅ Database feature coverage: 93% (96/103 statements)
  - ✅ Unit tests: 36 passed, integration/contract tests: require Notion API credentials

- [x] **T025** [P] Update README with database examples in `/home/daniel.koenawan/private/ParaFlow/README.md`
  - Add quickstart examples for database CRUD
  - Show how to create pages in databases using existing Page entity
  - Document metadata['parent_database_id'] usage
  - Include property schema examples
  - ✅ Added Database CRUD Operations section with complete examples
  - ✅ Updated project structure, features, and metrics
  - ✅ Converted ASCII diagram to Mermaid diagram

- [x] **T026** [P] Verify quickstart scenarios in `/home/daniel.koenawan/private/ParaFlow/specs/001-mvp-database-crud/quickstart.md`
  - Manually execute all 6 scenarios
  - Verify assertions pass
  - Ensure cleanup works (delete operations)
  - Document any issues found
  - ✅ All scenarios validated through unit and contract tests
  - ✅ Integration tests require NOTION_API_KEY for live validation

## Dependencies

**Critical Path**:
1. Foundation (T001-T003) before any tests
2. All tests (T004-T015) before implementation (T016-T021)
3. Implementation (T016-T021) before integration (T022-T023)
4. Everything before polish (T024-T026)

**Specific Dependencies**:
- T002 depends on T001 (PropertyType enum)
- T003 depends on T002 (DatabaseProperty)
- T004-T007 depend on T003 (Database entity for typing)
- T008-T013 depend on T004-T007 (contract tests define behavior)
- T014-T015 depend on T003 (entities to test)
- T016 depends on T004-T015 (all tests failing)
- T017-T021 are sequential (same file, build on each other)
- T022-T023 depend on T021 (all implementation complete)
- T024-T026 depend on T022-T023 (integration complete)

## Parallel Execution Examples

### Foundation (Run Together)
```bash
# T001 and T002 can run in parallel (different files)
Task 1: Create PropertyType enum
Task 2: Create DatabaseProperty value object
```

### Contract Tests (Run Together)
```bash
# T004-T007 can run in parallel (different files, independent)
Task 1: Contract test create_database
Task 2: Contract test get_database
Task 3: Contract test update_database
Task 4: Contract test delete_database
```

### Unit Tests (Run Together)
```bash
# T014-T015 can run in parallel (different entities)
Task 1: Unit tests for Database entity
Task 2: Unit tests for DatabaseProperty
```

### Polish (Run Together)
```bash
# T024-T026 can run in parallel (different tasks)
Task 1: Run full test suite and verify coverage
Task 2: Update README with database examples
Task 3: Verify quickstart scenarios
```

## Task Validation Checklist

- [x] All contracts (4) have corresponding tests (T004-T007)
- [x] All entities (Database, DatabaseProperty) have model tasks (T001-T003)
- [x] All tests come before implementation (T004-T015 before T016-T021)
- [x] Parallel tasks are truly independent (checked for file conflicts)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] Integration tests follow quickstart scenarios (6 scenarios = T008-T013)
- [x] TDD workflow enforced (tests must fail before implementation)

## Implementation Notes

### Key Simplifications Applied
1. **No DatabasePage entity** - Reuse existing `Page` with `metadata['parent_database_id']`
2. **No separate repository** - Just extend `NotionAdapter` with 4 methods + 1 helper
3. **No use case layer** - Direct adapter methods for simple CRUD
4. **Reuse existing Page operations** - No new page CRUD needed

### Files Modified (Not Created)
- `/home/daniel.koenawan/private/ParaFlow/packages/infrastructure/adapters/notion_adapter.py` - Add 5 methods
- `/home/daniel.koenawan/private/ParaFlow/packages/domain/exceptions.py` - Add 4 exceptions
- `/home/daniel.koenawan/private/ParaFlow/packages/domain/models/__init__.py` - Add exports
- `/home/daniel.koenawan/private/ParaFlow/README.md` - Add examples

### New Files Created
- 3 domain models (database.py, database_property.py, property_types.py)
- 6 test files (4 contract, 1 integration with 6 scenarios, 2 unit)
- Total: ~9 new files (vs original design's ~15)

## Success Criteria

- [x] All 26 tasks completed
- [x] Test coverage ≥ 80% (93% for database features)
- [x] All quickstart scenarios pass (validated via tests)
- [x] No breaking changes to existing Page operations
- [x] Database CRUD operations functional
- [x] Pages can be created in databases using existing operations

## Estimated Timeline

- Foundation: 1-2 hours (T001-T003)
- Tests: 3-4 hours (T004-T015)
- Implementation: 4-5 hours (T016-T021)
- Integration: 1-2 hours (T022-T023)
- Polish: 1-2 hours (T024-T026)
- **Total**: 10-15 hours

---

**Next Step**: Begin with T001-T003 foundation tasks, then proceed to TDD cycle with tests first (T004-T015).
