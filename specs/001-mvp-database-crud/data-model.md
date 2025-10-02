# Data Model: MVP Database CRUD

**Feature**: 001-mvp-database-crud
**Date**: 2025-10-02

## Design Philosophy

**Key Insight**: In Notion, a database page IS a page - just with structured properties. We reuse the existing `Page` entity and only add a `Database` entity for schema definition.

## Domain Entities

### 1. Database

**Purpose**: Represents a Notion database with schema definition

**Attributes**:
```python
@dataclass(frozen=True)
class Database:
    id: Optional[str]              # Notion database ID (None for new databases)
    title: str                     # Database title/name
    description: Optional[str]      # Database description
    properties: Dict[str, DatabaseProperty]  # Schema definition
    parent_id: Optional[str]        # Parent page/workspace ID
    created_at: Optional[datetime]  # Creation timestamp
    updated_at: Optional[datetime]  # Last update timestamp
    metadata: Dict[str, Any]        # Additional Notion metadata (URL, etc.)
```

**Business Rules**:
- Title is required (cannot be empty)
- At least one property must be defined
- ID is None for new databases, populated after creation
- Properties dict keys are property names, values are property schema definitions
- Parent ID determines where database is created (page or workspace root)

**State Transitions**:
- New → Created: Database created in Notion (ID assigned)
- Created → Updated: Properties/title modified
- Created → Archived: Database marked as archived (soft delete)

### 2. Page (Existing - Extended Usage)

**Purpose**: Represents any Notion page, including database pages

**Existing Attributes**:
```python
@dataclass(frozen=True)
class Page:
    id: Optional[str]
    title: str
    content: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    metadata: Dict[str, Any]  # For database pages: includes 'parent_database_id' and 'properties'
```

**Extended Usage for Database Pages**:
- `metadata['parent_database_id']`: Set when page is in a database
- `metadata['properties']`: Dict of property values when in database
- Regular pages: `metadata['parent_database_id']` is None/absent
- Database pages: Use existing Page CRUD operations with database-aware metadata

**Business Rules for Database Pages**:
- If `metadata['parent_database_id']` is set, page belongs to a database
- Properties in metadata must conform to database schema
- Existing Page operations (create/read/update/delete) work for database pages

## Value Objects

### 3. DatabaseProperty (Schema Definition)

**Purpose**: Defines a property's configuration in database schema

**Attributes**:
```python
@dataclass(frozen=True)
class DatabaseProperty:
    name: str                    # Property name
    property_type: PropertyType  # Enum: TITLE, TEXT, NUMBER, SELECT, etc.
    config: Dict[str, Any]       # Type-specific configuration
    is_required: bool = False    # Whether property is required
```

**Supported Property Types** (MVP):
- `TITLE`: Database title property (required, one per database)
- `RICH_TEXT`: Multi-line text
- `NUMBER`: Numeric values
- `SELECT`: Single selection from options
- `MULTI_SELECT`: Multiple selections from options
- `DATE`: Date or date range
- `CHECKBOX`: Boolean value
- `URL`: URL string
- `EMAIL`: Email string

**Configuration Examples**:
```python
# SELECT property
config = {
    "options": [
        {"name": "Option 1", "color": "blue"},
        {"name": "Option 2", "color": "green"}
    ]
}

# NUMBER property
config = {
    "format": "number"  # or "dollar", "percent", etc.
}

# DATE property
config = {} # No special config for MVP
```

### 4. PropertyValue (Data Values)

**Purpose**: Represents a typed value for a database property

**Attributes**:
```python
@dataclass(frozen=True)
class PropertyValue:
    property_type: PropertyType   # Type of this value
    value: Any                    # Actual value (type depends on property_type)
```

**Value Types by PropertyType**:
- `TITLE`: `str`
- `RICH_TEXT`: `str`
- `NUMBER`: `float` or `int`
- `SELECT`: `str` (selected option name)
- `MULTI_SELECT`: `List[str]` (selected option names)
- `DATE`: `datetime` or `Tuple[datetime, datetime]` (for ranges)
- `CHECKBOX`: `bool`
- `URL`: `str` (validated URL)
- `EMAIL`: `str` (validated email)

## Relationships

```
Database (1) ----< (N) Page (with parent_database_id in metadata)
    │
    └─> properties: Dict[str, DatabaseProperty]

Page (when in database)
    └─> metadata['properties']: Dict[str, Any]
        (keys must match parent Database.properties keys)
```

**Constraints**:
1. Page.metadata['parent_database_id'] must reference a valid Database.id (if set)
2. Page.metadata['properties'] keys must be subset of Database.properties keys
3. Page.metadata['properties'] values must match type of corresponding DatabaseProperty
4. Required properties in Database schema must have values in Page.metadata['properties']

## Domain Invariants

### Database Invariants
1. **Title Required**: `title` must not be empty string
2. **Properties Required**: `properties` dict must contain at least one entry
3. **Title Property**: Exactly one property must have `property_type == TITLE`
4. **Unique Property Names**: All property names must be unique within database

### Page Invariants (when in database)
1. **Database Reference**: `metadata['parent_database_id']` must be non-empty (if page is in database)
2. **Schema Compliance**: All property keys in `metadata['properties']` must exist in parent database schema
3. **Type Compliance**: All property values must match schema property types
4. **Required Properties**: All required properties from schema must have values

### PropertyValue Invariants
1. **Type Safety**: `value` type must match `property_type`
2. **SELECT Validation**: Select values must be from configured options
3. **URL Validation**: URL strings must be valid URLs
4. **EMAIL Validation**: Email strings must be valid email format

## Validation Rules

### Database Validation
- **On Create**:
  - Title is not empty
  - Has at least one property
  - Has exactly one TITLE property
  - Property names are unique

- **On Update**:
  - Same as create, plus:
  - ID must exist
  - Parent ID cannot be changed (if enforced by Notion API)

### Page Validation (when creating in database)
- **On Create**:
  - metadata['parent_database_id'] is not empty
  - All required properties have values in metadata['properties']
  - All property keys exist in database schema
  - All property values match schema types

- **On Update**:
  - Same as create, plus:
  - ID must exist
  - metadata['parent_database_id'] cannot be changed

### Property Validation
- **SELECT/MULTI_SELECT**: Values must be in configured options list
- **NUMBER**: Value must be numeric
- **DATE**: Value must be valid datetime
- **URL**: Value must be valid URL format
- **EMAIL**: Value must be valid email format
- **CHECKBOX**: Value must be boolean

## Error Scenarios

### Database Operations
1. **Create with empty title** → ValidationError
2. **Create without properties** → ValidationError
3. **Create with multiple TITLE properties** → ValidationError
4. **Update non-existent database** → DatabaseNotFoundError
5. **Delete database with pages** → Confirmation required, then cascade archive

### Page Operations (in database context)
1. **Create without required properties** → ValidationError + Confirmation prompt
2. **Create with invalid property types** → ValidationError
3. **Create with non-existent property names** → ValidationError
4. **Update non-existent page** → PageNotFoundError (existing error)
5. **Reference deleted database** → DatabaseNotFoundError

## Mapping to Notion API

### Database → Notion Database
```python
{
    "id": database.id,
    "title": [{"text": {"content": database.title}}],
    "description": [{"text": {"content": database.description}}] if database.description else [],
    "properties": {
        prop_name: {
            "type": prop.property_type.value.lower(),
            **prop.config
        }
        for prop_name, prop in database.properties.items()
    },
    "parent": {"type": "page_id", "page_id": database.parent_id} if database.parent_id else {"type": "workspace"},
}
```

### Page (in database) → Notion Page
```python
{
    "id": page.id,
    "parent": {"type": "database_id", "database_id": page.metadata['parent_database_id']},
    "properties": {
        prop_name: notion_property_value(prop_value)
        for prop_name, prop_value in page.metadata['properties'].items()
    }
}
```

**Note**: Existing Page CRUD operations in NotionPageRepositoryAdapter will be extended to handle database pages by detecting `metadata['parent_database_id']`

## Extension Points

Future enhancements can add:
1. Additional property types (person, files, formula, relation, rollup)
2. Property validation rules (min/max, regex patterns)
3. Database views and filters
4. Database sorting and grouping
5. Database permissions and sharing
6. Relation between databases
7. Formula and rollup properties
