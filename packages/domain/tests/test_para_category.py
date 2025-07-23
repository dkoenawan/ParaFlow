"""Tests for PARACategory enumeration."""

import pytest
from packages.domain.models.para_category import PARACategory


class TestPARACategory:
    """Test cases for PARACategory enumeration."""

    def test_enum_values(self):
        """Test that all PARA categories have correct string values."""
        assert PARACategory.PROJECT.value == "project"
        assert PARACategory.AREA.value == "area"
        assert PARACategory.RESOURCE.value == "resource"
        assert PARACategory.ARCHIVE.value == "archive"

    def test_string_representation(self):
        """Test string representation of categories."""
        assert str(PARACategory.PROJECT) == "project"
        assert str(PARACategory.AREA) == "area"
        assert str(PARACategory.RESOURCE) == "resource"
        assert str(PARACategory.ARCHIVE) == "archive"

    def test_from_string_valid(self):
        """Test creating categories from valid strings."""
        assert PARACategory.from_string("project") == PARACategory.PROJECT
        assert PARACategory.from_string("AREA") == PARACategory.AREA
        assert PARACategory.from_string("Resource") == PARACategory.RESOURCE
        assert PARACategory.from_string("ARCHIVE") == PARACategory.ARCHIVE

    def test_from_string_invalid(self):
        """Test creating categories from invalid strings raises ValueError."""
        with pytest.raises(ValueError, match="Invalid PARA category: invalid"):
            PARACategory.from_string("invalid")
        
        with pytest.raises(ValueError, match="Invalid PARA category: "):
            PARACategory.from_string("")

    def test_valid_transitions(self):
        """Test valid category transitions according to PARA methodology."""
        # PROJECT can transition to ARCHIVE or AREA
        assert PARACategory.PROJECT.can_transition_to(PARACategory.ARCHIVE)
        assert PARACategory.PROJECT.can_transition_to(PARACategory.AREA)
        assert not PARACategory.PROJECT.can_transition_to(PARACategory.RESOURCE)
        assert not PARACategory.PROJECT.can_transition_to(PARACategory.PROJECT)

        # AREA can transition to ARCHIVE only
        assert PARACategory.AREA.can_transition_to(PARACategory.ARCHIVE)
        assert not PARACategory.AREA.can_transition_to(PARACategory.PROJECT)
        assert not PARACategory.AREA.can_transition_to(PARACategory.RESOURCE)
        assert not PARACategory.AREA.can_transition_to(PARACategory.AREA)

        # RESOURCE can transition to ARCHIVE only
        assert PARACategory.RESOURCE.can_transition_to(PARACategory.ARCHIVE)
        assert not PARACategory.RESOURCE.can_transition_to(PARACategory.PROJECT)
        assert not PARACategory.RESOURCE.can_transition_to(PARACategory.AREA)
        assert not PARACategory.RESOURCE.can_transition_to(PARACategory.RESOURCE)

        # ARCHIVE can transition to any active category
        assert PARACategory.ARCHIVE.can_transition_to(PARACategory.PROJECT)
        assert PARACategory.ARCHIVE.can_transition_to(PARACategory.AREA)
        assert PARACategory.ARCHIVE.can_transition_to(PARACategory.RESOURCE)
        assert not PARACategory.ARCHIVE.can_transition_to(PARACategory.ARCHIVE)

    def test_get_description(self):
        """Test category descriptions."""
        assert PARACategory.PROJECT.get_description() == "Things with a deadline and specific outcome"
        assert PARACategory.AREA.get_description() == "Ongoing responsibilities to maintain"
        assert PARACategory.RESOURCE.get_description() == "Topics of ongoing interest"
        assert PARACategory.ARCHIVE.get_description() == "Inactive items from other categories"

    def test_is_active(self):
        """Test active category detection."""
        assert PARACategory.PROJECT.is_active()
        assert PARACategory.AREA.is_active()
        assert PARACategory.RESOURCE.is_active()
        assert not PARACategory.ARCHIVE.is_active()

    def test_requires_deadline(self):
        """Test deadline requirement detection."""
        assert PARACategory.PROJECT.requires_deadline()
        assert not PARACategory.AREA.requires_deadline()
        assert not PARACategory.RESOURCE.requires_deadline()
        assert not PARACategory.ARCHIVE.requires_deadline()

    def test_allows_indefinite_duration(self):
        """Test indefinite duration allowance."""
        assert not PARACategory.PROJECT.allows_indefinite_duration()
        assert PARACategory.AREA.allows_indefinite_duration()
        assert PARACategory.RESOURCE.allows_indefinite_duration()
        assert not PARACategory.ARCHIVE.allows_indefinite_duration()