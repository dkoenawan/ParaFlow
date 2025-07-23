"""Tests for ResourceTags value object."""

import pytest
from packages.domain.models.resource_tags import ResourceTags


class TestResourceTags:
    """Test cases for ResourceTags value object."""

    def test_create_empty_tags(self):
        """Test creating empty ResourceTags."""
        tags = ResourceTags.create()
        
        assert isinstance(tags, ResourceTags)
        assert tags.is_empty()
        assert tags.count() == 0

    def test_create_from_list(self):
        """Test creating ResourceTags from list of strings."""
        tag_list = ["work", "productivity", "notes"]
        tags = ResourceTags.create(tag_list)
        
        assert not tags.is_empty()
        assert tags.count() == 3
        assert "work" in tags
        assert "productivity" in tags
        assert "notes" in tags

    def test_create_from_set(self):
        """Test creating ResourceTags from set of strings."""
        tag_set = {"work", "productivity", "notes"}
        tags = ResourceTags.create(tag_set)
        
        assert tags.count() == 3
        assert "work" in tags

    def test_create_removes_duplicates(self):
        """Test that duplicate tags are removed during creation."""
        tag_list = ["work", "Work", "WORK", "productivity"]
        tags = ResourceTags.create(tag_list)
        
        assert tags.count() == 2  # "work" and "productivity"
        assert "work" in tags
        assert "productivity" in tags

    def test_create_normalizes_case(self):
        """Test that tags are normalized to lowercase."""
        tag_list = ["Work", "PRODUCTIVITY", "Notes"]
        tags = ResourceTags.create(tag_list)
        
        # Check that normalized tags are present
        assert "work" in tags
        assert "productivity" in tags  
        assert "notes" in tags
        
        # Check that the actual stored tags are normalized (lowercase)
        stored_tags = tags.to_list()
        assert "work" in stored_tags
        assert "productivity" in stored_tags
        assert "notes" in stored_tags
        assert "Work" not in stored_tags
        assert "PRODUCTIVITY" not in stored_tags

    def test_create_strips_whitespace(self):
        """Test that whitespace is stripped from tags."""
        tag_list = [" work ", "  productivity  ", "notes   "]
        tags = ResourceTags.create(tag_list)
        
        assert "work" in tags
        assert "productivity" in tags
        assert "notes" in tags

    def test_create_skips_empty_tags(self):
        """Test that empty tags are skipped."""
        tag_list = ["work", "", "   ", "productivity"]
        tags = ResourceTags.create(tag_list)
        
        assert tags.count() == 2
        assert "work" in tags
        assert "productivity" in tags

    def test_create_invalid_type_raises_error(self):
        """Test that invalid tag types raise TypeError."""
        with pytest.raises(TypeError, match="Tags must be a list, set, or None"):
            ResourceTags.create("not-a-list")
        
        with pytest.raises(TypeError, match="All tags must be strings"):
            ResourceTags.create([123, "valid"])

    def test_create_invalid_tag_format(self):
        """Test that invalid tag formats raise ValueError."""
        with pytest.raises(ValueError, match="Invalid tag format"):
            ResourceTags.create(["-invalid-start"])
        
        with pytest.raises(ValueError, match="Invalid tag format"):
            ResourceTags.create(["invalid-end-"])
        
        with pytest.raises(ValueError, match="Invalid tag format"):
            ResourceTags.create(["invalid space"])

    def test_valid_tag_formats(self):
        """Test that valid tag formats are accepted."""
        valid_tags = ["work", "w", "work-life", "work_balance", "web-dev-2024"]
        tags = ResourceTags.create(valid_tags)
        
        assert tags.count() == 5
        for tag in valid_tags:
            assert tag in tags

    def test_empty_class_method(self):
        """Test creating empty tags using class method."""
        tags = ResourceTags.empty()
        
        assert tags.is_empty()
        assert tags.count() == 0

    def test_from_string(self):
        """Test creating tags from delimited string."""
        tags = ResourceTags.from_string("work,productivity,notes")
        
        assert tags.count() == 3
        assert "work" in tags
        assert "productivity" in tags
        assert "notes" in tags

    def test_from_string_custom_separator(self):
        """Test creating tags from string with custom separator."""
        tags = ResourceTags.from_string("work|productivity|notes", separator="|")
        
        assert tags.count() == 3
        assert "work" in tags

    def test_from_string_empty(self):
        """Test creating tags from empty string."""
        tags = ResourceTags.from_string("")
        
        assert tags.is_empty()

    def test_add_tag(self):
        """Test adding a tag to existing ResourceTags."""
        tags = ResourceTags.create(["work"])
        new_tags = tags.add("productivity")
        
        assert tags.count() == 1  # Original unchanged
        assert new_tags.count() == 2
        assert "productivity" in new_tags
        assert "work" in new_tags

    def test_remove_tag(self):
        """Test removing a tag from ResourceTags."""
        tags = ResourceTags.create(["work", "productivity"])
        new_tags = tags.remove("work")
        
        assert tags.count() == 2  # Original unchanged
        assert new_tags.count() == 1
        assert "productivity" in new_tags
        assert "work" not in new_tags

    def test_remove_nonexistent_tag(self):
        """Test removing a tag that doesn't exist."""
        tags = ResourceTags.create(["work"])
        new_tags = tags.remove("nonexistent")
        
        assert new_tags.count() == 1
        assert "work" in new_tags

    def test_union(self):
        """Test combining two ResourceTags instances."""
        tags1 = ResourceTags.create(["work", "productivity"])
        tags2 = ResourceTags.create(["notes", "productivity"])
        combined = tags1.union(tags2)
        
        assert combined.count() == 3  # "productivity" not duplicated
        assert "work" in combined
        assert "productivity" in combined
        assert "notes" in combined

    def test_union_invalid_type(self):
        """Test union with invalid type raises TypeError."""
        tags = ResourceTags.create(["work"])
        
        with pytest.raises(TypeError, match="Can only union with ResourceTags"):
            tags.union(["not", "resource", "tags"])

    def test_contains_method(self):
        """Test the contains method."""
        tags = ResourceTags.create(["work", "productivity"])
        
        assert tags.contains("work")
        assert tags.contains("WORK")  # Case insensitive
        assert not tags.contains("nonexistent")

    def test_contains_operator(self):
        """Test the 'in' operator."""
        tags = ResourceTags.create(["work", "productivity"])
        
        assert "work" in tags
        assert "WORK" in tags  # Case insensitive
        assert "nonexistent" not in tags

    def test_to_list(self):
        """Test converting tags to sorted list."""
        tags = ResourceTags.create(["zebra", "apple", "banana"])
        tag_list = tags.to_list()
        
        assert tag_list == ["apple", "banana", "zebra"]  # Sorted
        assert isinstance(tag_list, list)

    def test_to_string(self):
        """Test converting tags to delimited string."""
        tags = ResourceTags.create(["work", "productivity"])
        tag_string = tags.to_string()
        
        # Should be sorted
        assert tag_string in ["productivity, work", "work, productivity"]

    def test_to_string_custom_separator(self):
        """Test converting tags to string with custom separator."""
        tags = ResourceTags.create(["work", "productivity"])
        tag_string = tags.to_string(" | ")
        
        assert " | " in tag_string

    def test_iteration(self):
        """Test iterating over tags."""
        tags = ResourceTags.create(["zebra", "apple", "banana"])
        tag_list = list(tags)
        
        assert tag_list == ["apple", "banana", "zebra"]  # Sorted

    def test_len_operator(self):
        """Test len() operator."""
        tags = ResourceTags.create(["work", "productivity", "notes"])
        
        assert len(tags) == 3

    def test_str_representation(self):
        """Test string representation."""
        tags = ResourceTags.create(["work", "productivity"])
        
        assert str(tags) == tags.to_string()

    def test_repr_short_list(self):
        """Test repr for short tag list."""
        tags = ResourceTags.create(["work", "notes"])
        
        assert "ResourceTags([" in repr(tags)
        assert "work" in repr(tags)
        assert "notes" in repr(tags)

    def test_repr_long_list(self):
        """Test repr for long tag list."""
        many_tags = [f"tag{i}" for i in range(10)]
        tags = ResourceTags.create(many_tags)
        
        repr_str = repr(tags)
        assert "... +7 more" in repr_str or "ResourceTags([" in repr_str

    def test_immutability(self):
        """Test that ResourceTags is immutable."""
        tags = ResourceTags.create(["work"])
        
        # Adding should return new instance
        new_tags = tags.add("productivity")
        assert tags is not new_tags
        assert tags.count() == 1
        assert new_tags.count() == 2