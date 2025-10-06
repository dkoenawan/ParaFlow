"""
Integration tests for database CRUD operations.

These tests follow the quickstart.md scenarios and test the complete
workflow from database creation through page management to cleanup.

Note: These tests require a valid Notion API key and will make real API calls.
They are marked as integration tests and should be skipped until implementation
is complete.
"""

import pytest
from packages.domain.models.database import Database
from packages.domain.models.database_property import DatabaseProperty
from packages.domain.models.property_types import PropertyType
from packages.domain.models.page import Page


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for complete database workflows."""

    @pytest.fixture
    def adapter(self):
        """
        Fixture to provide NotionAdapter instance.

        This will fail until NotionAdapter has database methods implemented.
        """
        pytest.skip("MUST FAIL: NotionAdapter database methods not implemented yet")
        # from packages.infrastructure.adapters.notion_adapter import NotionAdapter
        # return NotionAdapter()

    @pytest.fixture
    def created_database(self, adapter):
        """
        Fixture to create a test database for scenarios.

        Yields the created database and cleans it up after tests.
        """
        pytest.skip("MUST FAIL: create_database not implemented yet")

    def test_scenario_1_create_and_retrieve_database(self, adapter):
        """
        Scenario 1: Create and Retrieve Database

        Tests from quickstart.md Scenario 1:
        - Create database with TITLE and SELECT properties
        - Verify ID is assigned
        - Retrieve database and verify fields match
        """
        # Arrange
        database = Database(
            title="Quick Start Tasks",
            description="Test database for quickstart validation",
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE,
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

        # Act - This will fail until create_database is implemented
        pytest.skip("MUST FAIL: create_database not implemented yet")
        # created_db = adapter.create_database(database)
        #
        # # Assert
        # assert created_db.id is not None, "Database should have ID after creation"
        # assert created_db.title == "Quick Start Tasks"
        # assert len(created_db.properties) == 2
        #
        # # Retrieve and verify
        # retrieved_db = adapter.get_database(created_db.id)
        # assert retrieved_db.id == created_db.id
        # assert retrieved_db.title == created_db.title
        # assert "Name" in retrieved_db.properties
        # assert "Status" in retrieved_db.properties

    def test_scenario_2_update_database_schema(self, created_database, adapter):
        """
        Scenario 2: Update Database Schema

        Tests from quickstart.md Scenario 2:
        - Add a new property to existing database
        - Update description
        - Verify property count increases
        - Verify new property exists
        """
        # Arrange - Add Priority property
        updated_db = Database(
            id=created_database.id,
            title=created_database.title,
            description="Updated: Added priority field",
            properties={
                **created_database.properties,
                "Priority": DatabaseProperty(
                    name="Priority",
                    property_type=PropertyType.NUMBER,
                    config={"format": "number"}
                )
            }
        )

        # Act
        pytest.skip("MUST FAIL: update_database not implemented yet")
        # result_db = adapter.update_database(updated_db)
        #
        # # Assert
        # assert len(result_db.properties) == 3, "Should have 3 properties now"
        # assert "Priority" in result_db.properties
        # assert result_db.description == "Updated: Added priority field"

    def test_scenario_3_create_pages_in_database(self, created_database, adapter):
        """
        Scenario 3: Create Pages in Database

        Tests from quickstart.md Scenario 3:
        - Create pages using existing Page entity
        - Set parent_database_id in metadata
        - Set property values in metadata
        - Query pages from database
        """
        # Arrange - Create first page in database
        page1 = Page(
            title="Implement authentication",
            content="",
            metadata={
                "parent_database_id": created_database.id,
                "properties": {
                    "Status": "In Progress",
                    "Priority": 1
                }
            }
        )

        page2 = Page(
            title="Write documentation",
            metadata={
                "parent_database_id": created_database.id,
                "properties": {
                    "Status": "Todo",
                    "Priority": 2
                }
            }
        )

        # Act
        pytest.skip("MUST FAIL: create_page with database parent not implemented yet")
        # created_page1 = adapter.create_page(page1)
        # created_page2 = adapter.create_page(page2)
        #
        # # Assert
        # assert created_page1.id is not None
        # assert created_page1.metadata['parent_database_id'] == created_database.id
        # assert created_page2.id is not None
        #
        # # Query pages in database
        # pages = adapter.query_database_pages(created_database.id)
        # assert len(pages) >= 2

    def test_scenario_4_update_database_page(self, created_database, adapter):
        """
        Scenario 4: Update Database Page

        Tests from quickstart.md Scenario 4:
        - Update page properties using existing Page operations
        - Verify property values updated
        """
        # Arrange - Create a page first
        page = Page(
            title="Test Task",
            metadata={
                "parent_database_id": created_database.id,
                "properties": {
                    "Status": "Todo"
                }
            }
        )

        pytest.skip("MUST FAIL: update_page with database properties not implemented yet")
        # created_page = adapter.create_page(page)
        #
        # # Update page status
        # updated_page = Page(
        #     id=created_page.id,
        #     title="Test Task",
        #     metadata={
        #         "parent_database_id": created_database.id,
        #         "properties": {
        #             "Status": "Done"
        #         }
        #     }
        # )
        #
        # # Act
        # result_page = adapter.update_page(updated_page)
        #
        # # Assert
        # assert result_page.metadata['properties']['Status'] == "Done"

    def test_scenario_5_missing_required_property_validation(self, created_database, adapter):
        """
        Scenario 5: Missing Required Property Validation

        Tests from quickstart.md Scenario 5:
        - Attempt to create page without required title
        - Verify ValidationError is raised
        """
        from packages.domain.exceptions import ValidationError

        # Arrange - Page without title (required TITLE property)
        invalid_page = Page(
            title="",  # Empty title
            metadata={
                "parent_database_id": created_database.id,
                "properties": {
                    "Status": "Todo"
                }
            }
        )

        # Act & Assert
        pytest.skip("MUST FAIL: validation for database pages not implemented yet")
        # with pytest.raises(ValidationError, match="title|Name"):
        #     adapter.create_page(invalid_page)

    def test_scenario_6_delete_database_with_confirmation(self, adapter):
        """
        Scenario 6: Delete Database with Confirmation

        Tests from quickstart.md Scenario 6:
        - Create test database and pages
        - Delete pages first
        - Delete database with confirmation
        - Verify database is archived
        """
        # Arrange - Create database and pages
        database = Database(
            title="Temporary DB",
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE
                )
            }
        )

        pytest.skip("MUST FAIL: delete_database not implemented yet")
        # created_db = adapter.create_database(database)
        #
        # # Create test pages
        # page1 = Page(
        #     title="Page 1",
        #     metadata={"parent_database_id": created_db.id, "properties": {}}
        # )
        # page2 = Page(
        #     title="Page 2",
        #     metadata={"parent_database_id": created_db.id, "properties": {}}
        # )
        #
        # created_page1 = adapter.create_page(page1)
        # created_page2 = adapter.create_page(page2)
        #
        # # Act - Delete pages then database
        # adapter.delete_page(created_page1.id)
        # adapter.delete_page(created_page2.id)
        #
        # deleted = adapter.delete_database(created_db.id, confirm=True)
        #
        # # Assert
        # assert deleted is True
        #
        # # Verify deletion
        # retrieved = adapter.get_database(created_db.id)
        # assert retrieved is None or retrieved.metadata.get("archived") is True


@pytest.mark.integration
class TestDatabaseEdgeCases:
    """Additional edge case tests for database operations."""

    def test_database_without_parent_uses_workspace(self):
        """Test creating database without parent_id uses workspace as parent."""
        pytest.skip("MUST FAIL: create_database not implemented yet")

    def test_database_with_all_property_types(self):
        """Test database with all 9 supported property types."""
        pytest.skip("MUST FAIL: create_database not implemented yet")

    def test_update_nonexistent_database_raises_error(self):
        """Test updating non-existent database raises DatabaseNotFoundError."""
        pytest.skip("MUST FAIL: update_database not implemented yet")

    def test_delete_without_confirmation_requires_explicit_confirm(self):
        """Test delete without confirm=True does not delete."""
        pytest.skip("MUST FAIL: delete_database not implemented yet")

    def test_query_empty_database_returns_empty_list(self):
        """Test querying database with no pages returns empty list."""
        pytest.skip("MUST FAIL: query_database_pages not implemented yet")
