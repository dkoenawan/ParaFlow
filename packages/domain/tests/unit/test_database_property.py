"""
Unit tests for DatabaseProperty value object.

Tests validation, configuration handling, and Notion format conversion.
"""

import pytest
from packages.domain.models.database_property import DatabaseProperty
from packages.domain.models.property_types import PropertyType


class TestDatabaseProperty:
    """Unit tests for DatabaseProperty value object."""

    def test_create_minimal_property(self):
        """Test creating property with minimum required fields."""
        # Arrange & Act
        prop = DatabaseProperty(
            name="Title",
            property_type=PropertyType.TITLE
        )

        # Assert
        assert prop.name == "Title"
        assert prop.property_type == PropertyType.TITLE
        assert prop.config == {}
        assert prop.is_required is False

    def test_create_property_with_all_fields(self):
        """Test creating property with all fields populated."""
        # Arrange & Act
        prop = DatabaseProperty(
            name="Status",
            property_type=PropertyType.SELECT,
            config={"options": [{"name": "Active", "color": "green"}]},
            is_required=True
        )

        # Assert
        assert prop.name == "Status"
        assert prop.property_type == PropertyType.SELECT
        assert "options" in prop.config
        assert prop.is_required is True

    def test_validates_name_not_empty(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            DatabaseProperty(
                name="",
                property_type=PropertyType.TITLE
            )

    def test_validates_name_not_whitespace(self):
        """Test that whitespace-only name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            DatabaseProperty(
                name="   ",
                property_type=PropertyType.RICH_TEXT
            )

    def test_validates_property_type_is_enum(self):
        """Test that property_type must be PropertyType enum."""
        with pytest.raises(ValueError, match="must be PropertyType enum"):
            DatabaseProperty(
                name="Bad Type",
                property_type="title"  # String instead of enum
            )

    def test_select_property_requires_options(self):
        """Test SELECT property must have options in config."""
        with pytest.raises(ValueError, match="requires 'options'"):
            DatabaseProperty(
                name="Status",
                property_type=PropertyType.SELECT,
                config={}  # Missing options
            )

    def test_select_options_must_be_list(self):
        """Test SELECT options must be a list."""
        with pytest.raises(ValueError, match="options must be a list"):
            DatabaseProperty(
                name="Status",
                property_type=PropertyType.SELECT,
                config={"options": "not-a-list"}
            )

    def test_select_requires_at_least_one_option(self):
        """Test SELECT property must have at least one option."""
        with pytest.raises(ValueError, match="at least one option"):
            DatabaseProperty(
                name="Status",
                property_type=PropertyType.SELECT,
                config={"options": []}  # Empty list
            )

    def test_multi_select_requires_options(self):
        """Test MULTI_SELECT property must have options in config."""
        with pytest.raises(ValueError, match="requires 'options'"):
            DatabaseProperty(
                name="Tags",
                property_type=PropertyType.MULTI_SELECT,
                config={}
            )

    def test_multi_select_options_must_be_list(self):
        """Test MULTI_SELECT options must be a list."""
        with pytest.raises(ValueError, match="options must be a list"):
            DatabaseProperty(
                name="Tags",
                property_type=PropertyType.MULTI_SELECT,
                config={"options": {}}
            )

    def test_non_select_properties_dont_require_options(self):
        """Test that non-SELECT properties don't require options."""
        # These should all succeed without options
        for prop_type in [PropertyType.TITLE, PropertyType.RICH_TEXT,
                          PropertyType.NUMBER, PropertyType.DATE,
                          PropertyType.CHECKBOX, PropertyType.URL,
                          PropertyType.EMAIL]:
            prop = DatabaseProperty(
                name=f"Test {prop_type.value}",
                property_type=prop_type
            )
            assert prop.config == {}

    def test_to_notion_format_title(self):
        """Test TITLE property converts to Notion format."""
        # Arrange
        prop = DatabaseProperty(
            name="Name",
            property_type=PropertyType.TITLE
        )

        # Act
        notion_format = prop.to_notion_format()

        # Assert
        assert notion_format == {"type": "title"}

    def test_to_notion_format_select(self):
        """Test SELECT property converts to Notion format with options."""
        # Arrange
        options = [
            {"name": "Todo", "color": "red"},
            {"name": "Done", "color": "green"}
        ]
        prop = DatabaseProperty(
            name="Status",
            property_type=PropertyType.SELECT,
            config={"options": options}
        )

        # Act
        notion_format = prop.to_notion_format()

        # Assert
        assert notion_format["type"] == "select"
        assert "select" in notion_format
        assert notion_format["select"]["options"] == options

    def test_to_notion_format_multi_select(self):
        """Test MULTI_SELECT property converts to Notion format."""
        # Arrange
        options = [{"name": "urgent"}, {"name": "bug"}]
        prop = DatabaseProperty(
            name="Tags",
            property_type=PropertyType.MULTI_SELECT,
            config={"options": options}
        )

        # Act
        notion_format = prop.to_notion_format()

        # Assert
        assert notion_format["type"] == "multi_select"
        assert "multi_select" in notion_format
        assert notion_format["multi_select"]["options"] == options

    def test_to_notion_format_number(self):
        """Test NUMBER property converts to Notion format with format."""
        # Arrange
        prop = DatabaseProperty(
            name="Count",
            property_type=PropertyType.NUMBER,
            config={"format": "number"}
        )

        # Act
        notion_format = prop.to_notion_format()

        # Assert
        assert notion_format["type"] == "number"
        assert "number" in notion_format
        assert notion_format["number"]["format"] == "number"

    def test_to_notion_format_number_without_format(self):
        """Test NUMBER property without format config."""
        # Arrange
        prop = DatabaseProperty(
            name="Count",
            property_type=PropertyType.NUMBER
        )

        # Act
        notion_format = prop.to_notion_format()

        # Assert
        assert notion_format == {"type": "number"}

    def test_to_notion_format_simple_types(self):
        """Test simple property types convert to Notion format."""
        simple_types = [
            PropertyType.RICH_TEXT,
            PropertyType.DATE,
            PropertyType.CHECKBOX,
            PropertyType.URL,
            PropertyType.EMAIL
        ]

        for prop_type in simple_types:
            # Arrange
            prop = DatabaseProperty(
                name=f"Test {prop_type.value}",
                property_type=prop_type
            )

            # Act
            notion_format = prop.to_notion_format()

            # Assert
            assert notion_format == {"type": prop_type.value}

    def test_database_property_is_frozen(self):
        """Test that DatabaseProperty is immutable (frozen dataclass)."""
        # Arrange
        prop = DatabaseProperty(
            name="Frozen",
            property_type=PropertyType.TITLE
        )

        # Act & Assert - Attempting to modify should raise error
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            prop.name = "Modified"

    def test_str_representation(self):
        """Test string representation of property."""
        # Arrange
        prop = DatabaseProperty(
            name="Status",
            property_type=PropertyType.SELECT,
            config={"options": [{"name": "Active"}]},
            is_required=True
        )

        # Act
        str_repr = str(prop)

        # Assert
        assert "Status" in str_repr
        assert "select" in str_repr
        assert "(required)" in str_repr

    def test_str_representation_not_required(self):
        """Test string representation for non-required property."""
        # Arrange
        prop = DatabaseProperty(
            name="Notes",
            property_type=PropertyType.RICH_TEXT
        )

        # Act
        str_repr = str(prop)

        # Assert
        assert "Notes" in str_repr
        assert "rich_text" in str_repr
        assert "(required)" not in str_repr

    def test_config_defaults_to_empty_dict(self):
        """Test that config defaults to empty dict when not provided."""
        # Arrange & Act
        prop = DatabaseProperty(
            name="Simple",
            property_type=PropertyType.CHECKBOX
        )

        # Assert
        assert prop.config == {}
        assert isinstance(prop.config, dict)

    def test_is_required_defaults_to_false(self):
        """Test that is_required defaults to False when not provided."""
        # Arrange & Act
        prop = DatabaseProperty(
            name="Optional",
            property_type=PropertyType.DATE
        )

        # Assert
        assert prop.is_required is False
