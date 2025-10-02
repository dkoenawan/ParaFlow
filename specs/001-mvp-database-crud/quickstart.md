# Quickstart: MVP Database CRUD

**Feature**: 001-mvp-database-crud
**Purpose**: Validate database CRUD operations through user workflow scenarios
**Estimated Time**: 10-15 minutes

## Prerequisites

- [ ] Python 3.9+ installed
- [ ] Notion API key configured in `.env` (NOTION_API_KEY)
- [ ] Parent page ID for testing (NOTION_PARENT_PAGE_ID) - optional
- [ ] All dependencies installed (`pip install -e .`)
- [ ] All tests passing (`pytest`)

## Design Note

**Key Insight**: Database pages ARE pages in Notion. We use:
- New `Database` entity for schema/structure
- Existing `Page` entity for database pages (with `metadata['parent_database_id']`)
- Only 4 new operations: Database CRUD

## Test Scenarios

### Scenario 1: Create and Retrieve Database

**Objective**: Create a new database and verify it can be retrieved

```python
from packages.domain.models.database import Database, DatabaseProperty
from packages.domain.models.property_types import PropertyType
# Use existing infrastructure - just add database methods
from packages.infrastructure.adapters.notion_adapter import NotionAdapter

# Initialize adapter
adapter = NotionAdapter()

# Create database schema
database = Database(
    title="Quick Start Tasks",
    description="Test database for quickstart validation",
    properties={
        "Name": DatabaseProperty(
            name="Name",
            property_type=PropertyType.TITLE,
            config={},
            is_required=True
        ),
        "Status": DatabaseProperty(
            name="Status",
            property_type=PropertyType.SELECT,
            config={
                "options": [
                    {"name": "Todo", "color": "red"},
                    {"name": "In Progress", "color": "yellow"},
                    {"name": "Done", "color": "green"}
                ]
            }
        )
    }
)

# Execute create
created_db = adapter.create_database(database)

# Verify
assert created_db.id is not None, "Database should have ID after creation"
assert created_db.title == "Quick Start Tasks"
assert len(created_db.properties) == 2

# Retrieve
retrieved_db = adapter.get_database(created_db.id)
assert retrieved_db.id == created_db.id
assert retrieved_db.title == created_db.title

print(f"✅ Scenario 1 PASSED: Database created with ID {created_db.id}")
```

**Expected Result**: Database created and retrieved successfully

### Scenario 2: Update Database Schema

**Objective**: Add a new property to database schema

```python
# Add Priority property
updated_db = Database(
    id=created_db.id,
    title=created_db.title,
    description="Updated: Added priority field",
    properties={
        **created_db.properties,
        "Priority": DatabaseProperty(
            name="Priority",
            property_type=PropertyType.NUMBER,
            config={"format": "number"}
        )
    }
)

result_db = adapter.update_database(updated_db)

# Verify
assert len(result_db.properties) == 3, "Should have 3 properties now"
assert "Priority" in result_db.properties
assert result_db.description == "Updated: Added priority field"

print(f"✅ Scenario 2 PASSED: Database schema updated")
```

**Expected Result**: Database properties updated successfully

### Scenario 3: Create Pages in Database (Using Existing Page Operations)

**Objective**: Create pages in database using existing Page CRUD

```python
from packages.domain.models.page import Page

# Create first page in database - uses existing Page entity!
page1 = Page(
    title="Implement authentication",  # Maps to Name property (TITLE type)
    content="",  # Optional content blocks
    metadata={
        "parent_database_id": created_db.id,  # This makes it a database page
        "properties": {
            "Status": "In Progress",
            "Priority": 1
        }
    }
)

# Use EXISTING page operations - they already support database pages!
created_page1 = adapter.create_page(page1)
assert created_page1.id is not None
assert created_page1.metadata['parent_database_id'] == created_db.id

# Create second page
page2 = Page(
    title="Write documentation",
    metadata={
        "parent_database_id": created_db.id,
        "properties": {
            "Status": "Todo",
            "Priority": 2
        }
    }
)

created_page2 = adapter.create_page(page2)

# Query pages in database
pages = adapter.query_database_pages(created_db.id)
assert len(pages) >= 2

print(f"✅ Scenario 3 PASSED: Created {len(pages)} pages using existing Page operations")
```

**Expected Result**: Pages created in database using existing infrastructure

### Scenario 4: Update Database Page (Using Existing Page Operations)

**Objective**: Update page properties using existing Page update

```python
# Update page - uses existing Page operations!
updated_page = Page(
    id=created_page1.id,
    title="Implement authentication",
    metadata={
        "parent_database_id": created_db.id,
        "properties": {
            "Status": "Done",  # Updated status
            "Priority": 1
        }
    }
)

result_page = adapter.update_page(updated_page)

# Verify
assert result_page.metadata['properties']['Status'] == "Done"

print(f"✅ Scenario 4 PASSED: Page updated using existing operations")
```

**Expected Result**: Page properties updated successfully

### Scenario 5: Edge Case - Missing Required Property

**Objective**: Verify validation when creating page without required title

```python
from packages.domain.exceptions import ValidationError

# Attempt page without title (required TITLE property)
invalid_page = Page(
    title="",  # Empty title
    metadata={
        "parent_database_id": created_db.id,
        "properties": {
            "Status": "Todo"
        }
    }
)

try:
    adapter.create_page(invalid_page)
    assert False, "Should raise ValidationError"
except ValidationError as e:
    assert "title" in str(e).lower() or "Name" in str(e)
    print(f"✅ Scenario 5 PASSED: Validation caught missing required property")
```

**Expected Result**: ValidationError raised for missing title

### Scenario 6: Delete Database (With Confirmation)

**Objective**: Clean up by deleting database

```python
# Delete pages first (using existing operations)
adapter.delete_page(created_page1.id)
adapter.delete_page(created_page2.id)

# Delete database (requires confirmation for destructive operation)
deleted = adapter.delete_database(created_db.id, confirm=True)
assert deleted == True

# Verify
retrieved = adapter.get_database(created_db.id)
assert retrieved is None or retrieved.metadata.get("archived") == True

print(f"✅ Scenario 6 PASSED: Database deleted successfully")
```

**Expected Result**: All resources cleaned up

## Validation Checklist

- [ ] Database can be created with schema definition
- [ ] Database can be retrieved by ID
- [ ] Database schema can be updated (add/modify properties)
- [ ] Database can be deleted with confirmation
- [ ] Pages can be created in database (using existing Page operations)
- [ ] Pages can be updated (using existing Page operations)
- [ ] Pages can be queried from database
- [ ] Pages can be deleted (using existing Page operations)
- [ ] Validation errors raised for missing required properties
- [ ] Edge cases handled with user-friendly errors

## Success Criteria

All scenarios must:
1. Execute without unhandled exceptions
2. Meet assertion conditions
3. Complete in < 500ms per operation
4. Leave Notion workspace in clean state

## Key Simplifications from Original Design

1. **No DatabasePage entity** - Reuse existing `Page` with `metadata['parent_database_id']`
2. **No separate repository** - Just 4 methods added to existing NotionAdapter:
   - `create_database(database: Database) -> Database`
   - `get_database(database_id: str) -> Optional[Database]`
   - `update_database(database: Database) -> Database`
   - `delete_database(database_id: str, confirm: bool) -> bool`
3. **Reuse existing Page operations** - No new page operations needed!
4. **One new helper**: `query_database_pages(database_id: str) -> List[Page]`

## Performance Benchmarks

Expected execution times:
- Database create/update/delete: < 500ms
- Database retrieval: < 300ms
- Page operations: Use existing benchmarks (same operations)

## Next Steps

After quickstart validation:
1. Verify all 4 database operations work
2. Confirm existing Page operations handle database pages
3. Run full test suite (should be < 15 tests for MVP)
4. Update documentation
5. Create PR
