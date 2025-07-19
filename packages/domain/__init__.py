"""ParaFlow Domain Layer

This package contains the core domain logic for ParaFlow, following 
domain-driven design principles and hexagonal architecture.

The domain layer is technology-agnostic and contains:
- Domain entities and value objects
- Business rules and invariants
- Domain services
- Domain events

This package can be imported by:
- Application services (use cases)
- Infrastructure adapters
- User interface layers
"""

from .models import (
    ThoughtId,
    ContentText,
    ProcessingStatus,
    ThoughtContent,
)

__all__ = [
    "ThoughtId",
    "ContentText", 
    "ProcessingStatus",
    "ThoughtContent",
]

__version__ = "0.1.0"