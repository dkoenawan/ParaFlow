"""
Unit tests for Database entity.

Tests business logic, validation rules, and methods of the Database entity.
"""

import pytest
from datetime import datetime
from packages.domain.models.database import Database
from packages.domain.models.database_property import DatabaseProperty
from packages.domain.models.property_types import PropertyType


class TestDatabaseEntity:
    """Unit tests for Database entity."""

    def test_create_minimal_database(self):
        """Test creating database with minimum required fields."""
        # Arrange & Act
        database = Database(
            title="Test DB",
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE
                )
            }
        )

        # Assert
        assert database.title == "Test DB"
        assert len(database.properties) == 1
        assert database.id is None
        assert database.description is None
        assert database.parent_id is None

    def test_create_database_with_all_fields(self):
        """Test creating database with all fields populated."""
        # Arrange
        created_at = datetime(2025, 10, 2, 10, 0, 0)
        updated_at = datetime(2025, 10, 2, 11, 0, 0)

        # Act
        database = Database(
            id="db-123",
            title="Full DB",
            description="Complete database",
            properties={
                "Title": DatabaseProperty(
                    name="Title",
                    property_type=PropertyType.TITLE
                ),
                "Notes": DatabaseProperty(
                    name="Notes",
                    property_type=PropertyType.RICH_TEXT
                )
            },
            parent_id="parent-page-456",
            created_at=created_at,
            updated_at=updated_at,
            metadata={"url": "https://notion.so/db-123"}
        )

        # Assert
        assert database.id == "db-123"
        assert database.title == "Full DB"
        assert database.description == "Complete database"
        assert len(database.properties) == 2
        assert database.parent_id == "parent-page-456"
        assert database.created_at == created_at
        assert database.updated_at == updated_at
        assert database.metadata["url"] == "https://notion.so/db-123"

    def test_validates_title_required(self):
        """Test that empty title raises ValueError."""
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

    def test_validates_title_not_whitespace_only(self):
        """Test that whitespace-only title raises ValueError."""
        with pytest.raises(ValueError, match="title cannot be empty"):
            Database(
                title="   ",
                properties={
                    "Name": DatabaseProperty(
                        name="Name",
                        property_type=PropertyType.TITLE
                    )
                }
            )

    def test_validates_at_least_one_property(self):
        """Test that database without properties raises ValueError."""
        with pytest.raises(ValueError, match="at least one property"):
            Database(
                title="No Props",
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
                title="Two Titles",
                properties={
                    "Name": DatabaseProperty(
                        name="Name",
                        property_type=PropertyType.TITLE
                    ),
                    "Title": DatabaseProperty(
                        name="Title",
                        property_type=PropertyType.TITLE
                    )
                }
            )

    def test_has_id_returns_false_when_no_id(self):
        """Test has_id() returns False for new database."""
        # Arrange
        database = Database(
            title="New DB",
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE
                )
            }
        )

        # Assert
        assert database.has_id() is False

    def test_has_id_returns_false_for_empty_id(self):
        """Test has_id() returns False for empty string ID."""
        # Arrange
        database = Database(
            id="",
            title="Empty ID",
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE
                )
            }
        )

        # Assert
        assert database.has_id() is False

    def test_has_id_returns_true_when_id_present(self):
        """Test has_id() returns True for persisted database."""
        # Arrange
        database = Database(
            id="db-456",
            title="Persisted DB",
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE
                )
            }
        )

        # Assert
        assert database.has_id() is True

    def test_is_valid_returns_true_for_valid_database(self):
        """Test is_valid() returns True for valid database."""
        # Arrange
        database = Database(
            title="Valid DB",
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE
                ),
                "Status": DatabaseProperty(
                    name="Status",
                    property_type=PropertyType.SELECT,
                    config={"options": [{"name": "Active"}]}
                )
            }
        )

        # Assert
        assert database.is_valid() is True

    def test_get_title_property_name_returns_correct_name(self):
        """Test get_title_property_name() returns the TITLE property name."""
        # Arrange
        database = Database(
            title="Test",
            properties={
                "Task Name": DatabaseProperty(
                    name="Task Name",
                    property_type=PropertyType.TITLE
                ),
                "Description": DatabaseProperty(
                    name="Description",
                    property_type=PropertyType.RICH_TEXT
                )
            }
        )

        # Act
        title_prop_name = database.get_title_property_name()

        # Assert
        assert title_prop_name == "Task Name"

    def test_get_title_property_name_returns_none_when_no_title(self):
        """Test get_title_property_name() returns None if no TITLE property."""
        # This should not be possible with validation, but test the method
        # Arrange - We can't actually create this through normal means
        # So this tests the method's robustness

        # Since validation prevents this, skip or test the method directly
        pytest.skip("Cannot create database without TITLE property due to validation")

    def test_database_is_frozen_dataclass(self):
        """Test that Database is immutable (frozen dataclass)."""
        # Arrange
        database = Database(
            title="Frozen DB",
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE
                )
            }
        )

        # Act & Assert - Attempting to modify should raise error
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            database.title = "Modified"

    def test_str_representation_without_id(self):
        """Test string representation for database without ID."""
        # Arrange
        database = Database(
            title="Test DB",
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE
                )
            }
        )

        # Act
        str_repr = str(database)

        # Assert
        assert "id=None" in str_repr
        assert "Test DB" in str_repr
        assert "properties=1" in str_repr

    def test_str_representation_with_id(self):
        """Test string representation for persisted database."""
        # Arrange
        database = Database(
            id="db-789",
            title="Persisted DB",
            properties={
                "Name": DatabaseProperty(
                    name="Name",
                    property_type=PropertyType.TITLE
                ),
                "Tags": DatabaseProperty(
                    name="Tags",
                    property_type=PropertyType.MULTI_SELECT,
                    config={"options": [{"name": "urgent"}]}
                )
            }
        )

        # Act
        str_repr = str(database)

        # Assert
        assert "id=db-789" in str_repr
        assert "Persisted DB" in str_repr
        assert "properties=2" in str_repr
