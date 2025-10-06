"""
Database property value object for schema definitions.

This module defines the DatabaseProperty value object used to represent
property schema definitions in Notion databases.
"""

from dataclasses import dataclass, field
from typing import Dict, Any

from .property_types import PropertyType


@dataclass(frozen=True)
class DatabaseProperty:
    """
    Value object representing a property schema definition in a database.

    This class defines the structure and configuration of a single property
    in a Notion database schema. Properties define the types of data that
    can be stored in database pages.

    Attributes:
        name: The property name (must be unique within database)
        property_type: The type of this property (from PropertyType enum)
        config: Type-specific configuration (e.g., options for SELECT)
        is_required: Whether this property must have a value in pages
    """

    name: str
    property_type: PropertyType
    config: Dict[str, Any] = field(default_factory=dict)
    is_required: bool = False

    def __post_init__(self) -> None:
        """
        Validate property schema after initialization.

        Raises:
            ValueError: If name is empty or property_type is invalid
        """
        if not self.name or not self.name.strip():
            raise ValueError("Property name cannot be empty")

        if not isinstance(self.property_type, PropertyType):
            raise ValueError(
                f"property_type must be PropertyType enum, got {type(self.property_type)}"
            )

        # Validate SELECT/MULTI_SELECT have options
        if self.property_type in (PropertyType.SELECT, PropertyType.MULTI_SELECT):
            if "options" not in self.config:
                raise ValueError(
                    f"{self.property_type.value} property requires 'options' in config"
                )
            if not isinstance(self.config["options"], list):
                raise ValueError("options must be a list")
            if not self.config["options"]:
                raise ValueError(
                    f"{self.property_type.value} property requires at least one option"
                )

    def to_notion_format(self) -> Dict[str, Any]:
        """
        Convert property schema to Notion API format.

        Returns:
            Dictionary in Notion API property schema format
        """
        type_str = self.property_type.value
        notion_format: Dict[str, Any] = {}

        # Add type-specific configuration
        if self.property_type == PropertyType.SELECT and "options" in self.config:
            notion_format[type_str] = {"options": self.config["options"]}
        elif (
            self.property_type == PropertyType.MULTI_SELECT and "options" in self.config
        ):
            notion_format[type_str] = {"options": self.config["options"]}
        elif self.property_type == PropertyType.NUMBER and "format" in self.config:
            notion_format[type_str] = {"format": self.config["format"]}
        else:
            # For other types (title, rich_text, date, checkbox, etc.), just include empty object
            notion_format[type_str] = {}

        return notion_format

    def __str__(self) -> str:
        """String representation of the property."""
        required_str = " (required)" if self.is_required else ""
        return f"DatabaseProperty(name='{self.name}', type={self.property_type.value}{required_str})"
