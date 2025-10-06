
# Implementation Plan: MVP Database CRUD

**Branch**: `001-mvp-database-crud` | **Date**: 2025-10-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/daniel.koenawan/private/ParaFlow/specs/001-mvp-database-crud/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Extend the existing Notion API MVP to support database CRUD operations (4 operations only). Database pages ARE pages in Notion, so we reuse the existing `Page` entity and operations. This MVP adds only a `Database` entity for schema definition and 4 new adapter methods, maximizing reuse of existing infrastructure.

## Technical Context
**Language/Version**: Python 3.9+ (existing project uses 3.9-3.12)
**Primary Dependencies**: notion-client, pydantic, python-dotenv, pytest
**Storage**: Notion API (remote) - no local storage required
**Testing**: pytest with pytest-asyncio, pytest-cov, pytest-mock
**Target Platform**: Python library/package (cross-platform)
**Project Type**: Single monorepo with hexagonal architecture (packages/)
**Performance Goals**: <500ms response time for Notion API operations
**Constraints**: API rate limits from Notion, API key authentication only
**Scale/Scope**: Minimal extension - add 4 database operations + 1 query helper (reuse existing Page operations for database pages)

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Hexagonal Architecture First
✅ **PASS** - Minimal extension of existing architecture:
- Domain layer: New `Database` entity only (reuse existing `Page` for database pages)
- Infrastructure layer: Add 4 methods to existing NotionAdapter
- NO new ports/repositories needed (just extend adapter)
- Simpler than original design - maximum reuse

### II. Test-Driven Development
✅ **PASS** - TDD workflow planned:
- Contract tests first (API schemas)
- Integration tests for user workflows
- Unit tests for domain logic (80% coverage target)
- Red-Green-Refactor cycle enforced

### III. PARA Framework Alignment
✅ **PASS** - Database operations support PARA:
- Databases can represent Projects, Areas, or Resources
- Database pages can be categorized within PARA structure
- Extension of existing PARA categorization system

### IV. Clean Code & Documentation
✅ **PASS** - Standards maintained:
- PEP 8 compliance (black, isort configured)
- Type hints required (mypy strict mode)
- Docstrings for all public APIs
- README updates for new functionality

### V. Async-First Design
⚠️ **DEFER** - Async operations:
- Current MVP uses synchronous notion-client
- All new operations will follow existing synchronous pattern
- Future async migration planned separately
- Justification: Consistency with existing Page operations MVP

## Project Structure

### Documentation (this feature)
```
specs/001-mvp-database-crud/
├── spec.md              # Feature specification
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
packages/
├── domain/
│   ├── models/
│   │   ├── page.py                    # Existing - reused for database pages!
│   │   ├── database.py                # NEW - Database entity only
│   │   ├── database_property.py       # NEW - Property schema value object
│   │   └── property_types.py          # NEW - PropertyType enum
│   └── ports/
│       └── page_repository.py         # Existing - no changes needed
│
├── infrastructure/
│   └── adapters/
│       └── notion_adapter.py          # EXTEND - Add 4 database methods + 1 query helper
│
└── interfaces/
    └── cli/
        └── database_commands.py       # NEW - Optional CLI for databases

packages/domain/tests/
├── unit/
│   ├── test_database.py               # NEW - Database model tests
│   └── test_database_property.py      # NEW - Property tests
├── integration/
│   └── test_database_integration.py   # NEW - 6 quickstart scenarios
└── contract/
    └── test_database_contracts.py     # NEW - 4 database operation contracts
```

**Structure Decision**: Minimal extension approach. Add only `Database` entity and value objects to domain layer. Extend existing `NotionAdapter` with 4 database methods. Reuse existing `Page` entity for database pages by using `metadata['parent_database_id']`. This maximizes code reuse and minimizes new files (only ~6 new files vs original design's ~12).

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
1. Load `.specify/templates/tasks-template.md` as base
2. Generate tasks from Phase 1 artifacts:
   - **From data-model.md**:
     - Create `Database` entity only (no DatabasePage - reuse Page!)
     - Create `DatabaseProperty` and `PropertyType` value objects [P]
   - **From contracts/database_operations.yaml**:
     - Contract tests for 4 database operations only [P]
   - **From quickstart.md**:
     - Integration tests for 6 scenarios (including page operations)
   - **Implementation tasks**:
     - Extend existing NotionAdapter with 4 database methods
     - Add query helper for database pages

**Ordering Strategy** (TDD-compliant, simplified):
1. **Foundation** (Parallel):
   - Task 1: Create PropertyType enum [P]
   - Task 2: Create DatabaseProperty value object [P]

2. **Domain Model**:
   - Task 3: Create Database entity with unit tests

3. **Contract Tests** (Parallel):
   - Tasks 4-7: Contract tests for 4 database operations (create/read/update/delete) [P]

4. **Integration Tests** (Sequential):
   - Tasks 8-13: One task per quickstart scenario (6 scenarios)

5. **Infrastructure Implementation**:
   - Task 14: Extend NotionAdapter with create_database/get_database
   - Task 15: Extend NotionAdapter with update_database/delete_database
   - Task 16: Add query_database_pages helper
   - Task 17: Update existing create_page to handle database parent

6. **Interface Layer** (Optional):
   - Task 18: Add CLI commands for database operations (optional)

7. **Documentation & Cleanup**:
   - Task 19: Update README with database examples
   - Task 20: Final test run and coverage check

**Estimated Output**: ~20 numbered, dependency-ordered tasks in tasks.md (down from 27!)

**Key Simplifications**:
- No DatabasePage entity (reuse Page)
- No separate repository/port (extend existing adapter)
- No use case layer needed (adapter methods are simple CRUD)
- Fewer tests needed (4 contract tests vs 8)

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Async-First Design (deferred) | Maintain consistency with existing MVP | Mixing async/sync in same codebase creates confusion; bulk migration to async is separate effort |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
