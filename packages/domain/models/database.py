"""
Database domain model for PARA framework.

This module defines the Database entity representing a Notion database
with schema definition and metadata.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

from .database_property import DatabaseProperty
from .property_types import PropertyType


@dataclass(frozen=True)
class Database:
    """
    Domain entity representing a Notion database.

    A database is a structured container that holds pages with typed properties.
    The database defines the schema (property definitions) that all pages within
    it must conform to.

    Attributes:
        id: Notion database ID (None for new databases)
        title: Database title/name (required)
        description: Optional database description
        properties: Schema definition mapping property names to their definitions
        parent_id: Parent page/workspace ID where database is located
        created_at: Creation timestamp
        updated_at: Last update timestamp
        metadata: Additional Notion metadata (URL, etc.)
    """

    title: str
    properties: Dict[str, DatabaseProperty]
    id: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate database after initialization.

        Raises:
            ValueError: If validation fails
        """
        # Validate title
        if not self.title or not self.title.strip():
            raise ValueError("Database title cannot be empty")

        # Validate properties
        if not self.properties:
            raise ValueError("Database must have at least one property")

        # Validate exactly one TITLE property
        title_props = [
            prop
            for prop in self.properties.values()
            if prop.property_type == PropertyType.TITLE
        ]
        if len(title_props) == 0:
            raise ValueError("Database must have exactly one TITLE property")
        if len(title_props) > 1:
            raise ValueError(
                f"Database must have exactly one TITLE property, found {len(title_props)}"
            )

        # Validate property names are unique (already guaranteed by Dict, but good to be explicit)
        if len(self.properties) != len(set(self.properties.keys())):
            raise ValueError("All property names must be unique")

    def has_id(self) -> bool:
        """
        Check if the database has been persisted (has an ID).

        Returns:
            True if database has an ID, False otherwise
        """
        return self.id is not None and self.id.strip() != ""

    def is_valid(self) -> bool:
        """
        Check if the database is valid.

        Returns:
            True if database passes all validation rules
        """
        try:
            # Re-run validation logic
            if not self.title or not self.title.strip():
                return False
            if not self.properties:
                return False

            title_props = [
                prop
                for prop in self.properties.values()
                if prop.property_type == PropertyType.TITLE
            ]
            if len(title_props) != 1:
                return False

            return True
        except Exception:
            return False

    def get_title_property_name(self) -> Optional[str]:
        """
        Get the name of the TITLE property.

        Returns:
            Name of the TITLE property, or None if not found
        """
        for name, prop in self.properties.items():
            if prop.property_type == PropertyType.TITLE:
                return name
        return None

    def __str__(self) -> str:
        """String representation of the database."""
        id_str = f"id={self.id}" if self.has_id() else "id=None"
        prop_count = len(self.properties)
        return f"Database({id_str}, title='{self.title}', properties={prop_count})"
