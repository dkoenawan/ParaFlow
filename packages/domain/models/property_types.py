"""
Property types for Notion database schemas.

This module defines the PropertyType enum representing all supported
property types in Notion databases for the MVP.
"""

from enum import Enum


class PropertyType(Enum):
    """
    Enumeration of supported Notion database property types.

    This enum defines the property types that can be used in database schemas.
    Each type corresponds to a specific Notion API property type.

    Attributes:
        TITLE: Title property (required, one per database)
        RICH_TEXT: Multi-line rich text content
        NUMBER: Numeric values
        SELECT: Single selection from predefined options
        MULTI_SELECT: Multiple selections from predefined options
        DATE: Date or date range values
        CHECKBOX: Boolean checkbox values
        URL: URL string values
        EMAIL: Email string values
    """

    TITLE = "title"
    RICH_TEXT = "rich_text"
    NUMBER = "number"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    DATE = "date"
    CHECKBOX = "checkbox"
    URL = "url"
    EMAIL = "email"

    def __str__(self) -> str:
        """Return the property type value as string."""
        return self.value
