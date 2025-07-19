# Domain Model Documentation

This document provides detailed documentation of ParaFlow's core domain model, implemented following domain-driven design (DDD) principles and hexagonal architecture.

## Overview

The domain model represents the core business logic for thought streaming and processing within the PARA framework. All domain entities are immutable, type-safe, and encapsulate business rules.

## Entities

### ThoughtContent

The primary aggregate root representing a user's thought for processing.

**Location**: `packages/domain/models/thought_content.py`

**Attributes**:
- `id: ThoughtId` - Unique identifier
- `title: str` - Brief title or summary  
- `content: ContentText` - Free-form thought content
- `created_date: datetime` - Creation timestamp
- `processed: bool` - Processing completion flag
- `processing_status: ProcessingStatus` - Current processing state
- `project_tag: str | None` - Optional user-assigned project tag
- `area_tag: str | None` - Optional user-assigned area tag

**Key Methods**:
- `create()` - Factory method for new thoughts
- `create_from_text()` - Factory method from plain text
- `mark_processed()` - Transition to processed state
- `update_status()` - Update processing status with validation
- `add_tags()` - Add project/area tags
- `matches_criteria()` - Query method for filtering

**Business Rules**:
- Immutable once created (frozen dataclass)
- Status transitions must be valid per ProcessingStatus rules
- Title and content cannot be empty
- Created date defaults to UTC now if not provided
- Processing status defaults to NEW for new thoughts

## Value Objects

### ThoughtId

Type-safe unique identifier for thoughts.

**Location**: `packages/domain/models/thought_id.py`

**Features**:
- UUID4-based generation
- String representation and conversion
- Immutable value object
- Type safety for thought identification

### ContentText

Value object representing validated thought content.

**Location**: `packages/domain/models/content_text.py`

**Features**:
- String validation and type checking
- Content manipulation methods (strip, truncate, search)
- No length limits to support thought streaming
- Unicode and multiline content support
- Immutable value semantics

**Key Methods**:
- `create()` - Factory method from string
- `empty()` - Create empty content
- `is_empty()` - Check for empty/whitespace content
- `truncated()` - Display truncation (non-destructive)
- `contains_text()` - Content search functionality

## Enumerations

### ProcessingStatus

Lifecycle management for thought processing states.

**Location**: `packages/domain/models/processing_status.py`

**Values**:
- `NEW` - New thought awaiting processing
- `PROCESSING` - Currently being analyzed by Claude
- `COMPLETED` - Successfully processed and categorized  
- `FAILED` - Processing failed, requires attention
- `SKIPPED` - Duplicate or invalid content

**State Transitions**:
- NEW → PROCESSING, SKIPPED
- PROCESSING → COMPLETED, FAILED
- FAILED → PROCESSING (retry allowed)
- COMPLETED/SKIPPED are final states

**Methods**:
- `can_transition_to()` - Validate state transitions
- `from_string()` - Create from string (case-insensitive)
- `__str__()` - String representation

## Design Principles

### Immutability

All domain objects use Python's `@dataclass(frozen=True)` to ensure immutability:
- Prevents accidental mutation
- Enables safe sharing across boundaries
- Simplifies concurrent access patterns
- Enforces explicit state changes through methods

### Type Safety

Modern Python typing with union types:
- `str | None` instead of `Optional[str]`
- Requires Python 3.12+
- Strong typing prevents runtime errors
- Clear intent through type annotations

### Business Rule Enforcement

Domain logic is enforced at the entity level:
- Status transition validation
- Content validation
- Invariant preservation
- Clear error messages for violations

### Value Object Patterns

Value objects provide:
- Type safety (ThoughtId vs raw strings)
- Behavior encapsulation (ContentText operations)
- Immutable semantics
- Rich comparison and representation

## Testing Strategy

The domain model includes comprehensive test coverage:

- **Unit tests**: 76+ tests covering all functionality
- **Edge cases**: Empty content, invalid transitions, Unicode
- **Business rules**: Status transitions, validation logic
- **Value objects**: Immutability, equality, string conversion
- **Factory methods**: Object creation scenarios

**Test Organization**:
```
packages/domain/tests/
├── test_thought_content.py    # ThoughtContent entity tests
├── test_thought_id.py         # ThoughtId value object tests  
├── test_content_text.py       # ContentText value object tests
└── test_processing_status.py  # ProcessingStatus enum tests
```

## Usage Examples

### Creating Thoughts

```python
from packages.domain.models import ThoughtContent, ThoughtId

# Create from text
thought = ThoughtContent.create_from_text(
    title="Project idea",
    content="Build an AI-powered personal assistant for PARA",
    project_tag="ParaFlow",
    area_tag="Software Development"
)

# Create with explicit values
thought = ThoughtContent.create(
    id=ThoughtId.generate(),
    title="Meeting notes",
    content=ContentText.create("Discussed project timeline..."),
    project_tag="Q1 Planning"
)
```

### Status Management

```python
# Check valid transitions
if thought.processing_status.can_transition_to(ProcessingStatus.PROCESSING):
    thought = thought.update_status(ProcessingStatus.PROCESSING)

# Mark as processed
processed_thought = thought.mark_processed()
```

### Content Operations

```python
content = ContentText.create("Long thought content...")

# Check properties
if not content.is_empty():
    length = content.length()
    
# Display truncation
summary = content.truncated(100)

# Search content
has_keyword = content.contains_text("PARA", case_sensitive=False)
```

## Future Considerations

### Planned Extensions

- **Categorization**: AI-powered PARA categorization
- **Versioning**: Thought evolution tracking  
- **Metadata**: Rich metadata and tagging
- **Relationships**: Thought linking and dependencies
- **Search**: Advanced search and filtering capabilities

### Integration Points

- **Infrastructure Layer**: Persistence adapters
- **Application Layer**: Use case orchestration
- **API Layer**: REST/GraphQL endpoints
- **Event System**: Domain event publishing

The domain model serves as the stable core that remains independent of external concerns while providing rich behavior for thought management within the PARA framework.