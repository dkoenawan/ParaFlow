"""
Contract test for create_database operation.

Tests that Database entity maps correctly to Notion API format for creation.
"""

import pytest
from datetime import datetime
from packages.domain.models.database import Database
from packages.domain.models.database_property import DatabaseProperty
from packages.domain.models.property_types import PropertyType


class TestCreateDatabaseContract:
    """Contract tests for database creation operation."""

    def test_database_to_notion_format_basic(self):
        """Test basic database with TITLE and TEXT properties maps to Notion format."""
        # Arrange
        database = Database(
            title="Test Database",
            description="Test description",
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE,
                    is_required=True
                ),
                "Notes": DatabaseProperty(
                    name="Notes",
                    property_type=PropertyType.RICH_TEXT
                )
            }
        )

        # Act - This will fail until NotionAdapter.create_database is implemented
        # Expected Notion API format for database creation
        expected_format = {
            "title": [{"text": {"content": "Test Database"}}],
            "description": [{"text": {"content": "Test description"}}],
            "properties": {
                "Name": {
                    "type": "title"
                },
                "Notes": {
                    "type": "rich_text"
                }
            }
        }

        # Assert - This test MUST FAIL initially (no implementation yet)
        # When NotionAdapter.create_database is implemented, it should:
        # 1. Accept Database entity
        # 2. Map to expected_format
        # 3. Make POST request to Notion API
        # 4. Return Database with ID populated
        pytest.skip("MUST FAIL: create_database not implemented yet")

    def test_database_with_select_property(self):
        """Test database with SELECT property includes options in Notion format."""
        # Arrange
        database = Database(
            title="Status Tracker",
            properties={
                "Task": DatabaseProperty(
                    name="Task",
                    property_type=PropertyType.TITLE
                ),
                "Status": DatabaseProperty(
                    name="Status",
                    property_type=PropertyType.SELECT,
                    config={
                        "options": [
                            {"name": "Todo", "color": "red"},
                            {"name": "Done", "color": "green"}
                        ]
                    }
                )
            }
        )

        # Assert - Expected Notion format for SELECT property
        expected_properties = {
            "Task": {
                "type": "title"
            },
            "Status": {
                "type": "select",
                "select": {
                    "options": [
                        {"name": "Todo", "color": "red"},
                        {"name": "Done", "color": "green"}
                    ]
                }
            }
        }

        pytest.skip("MUST FAIL: create_database not implemented yet")

    def test_database_with_parent_id(self):
        """Test database with parent page ID sets correct parent in Notion format."""
        # Arrange
        database = Database(
            title="Child Database",
            parent_id="parent-page-123",
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE
                )
            }
        )

        # Assert - Expected parent format
        expected_parent = {
            "type": "page_id",
            "page_id": "parent-page-123"
        }

        pytest.skip("MUST FAIL: create_database not implemented yet")

    def test_database_without_parent_uses_workspace(self):
        """Test database without parent ID uses workspace as parent."""
        # Arrange
        database = Database(
            title="Root Database",
            parent_id=None,
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE
                )
            }
        )

        # Assert - Expected workspace parent
        expected_parent = {
            "type": "workspace"
        }

        pytest.skip("MUST FAIL: create_database not implemented yet")

    def test_validates_title_required(self):
        """Test that empty title raises validation error."""
        with pytest.raises(ValueError, match="title cannot be empty"):
            Database(
                title="",
                properties={
                    "Name": DatabaseProperty(
                        name="Name",
                        property_type=PropertyType.TITLE
                    )
                }
            )

    def test_validates_properties_required(self):
        """Test that database without properties raises validation error."""
        with pytest.raises(ValueError, match="at least one property"):
            Database(
                title="Invalid DB",
                properties={}
            )

    def test_validates_exactly_one_title_property(self):
        """Test that database must have exactly one TITLE property."""
        # No TITLE property
        with pytest.raises(ValueError, match="exactly one TITLE property"):
            Database(
                title="No Title Prop",
                properties={
                    "Notes": DatabaseProperty(
                        name="Notes",
                        property_type=PropertyType.RICH_TEXT
                    )
                }
            )

        # Multiple TITLE properties
        with pytest.raises(ValueError, match="exactly one TITLE property"):
            Database(
                title="Multiple Titles",
                properties={
                    "Name": DatabaseProperty(
                        name="Name",
                        property_type=PropertyType.TITLE
                    ),
                    "Title2": DatabaseProperty(
                        name="Title2",
                        property_type=PropertyType.TITLE
                    )
                }
            )
