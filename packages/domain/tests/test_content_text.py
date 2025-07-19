"""Tests for ContentText value object."""

import pytest
from packages.domain.models.content_text import ContentText


class TestContentText:
    """Test cases for ContentText value object."""

    def test_create_with_string(self) -> None:
        """Test creating ContentText with a string."""
        content = ContentText("Hello world")
        
        assert content.value == "Hello world"
        assert isinstance(content.value, str)

    def test_create_class_method(self) -> None:
        """Test creating ContentText using create class method."""
        content = ContentText.create("Test content")
        
        assert content.value == "Test content"

    def test_empty_class_method(self) -> None:
        """Test creating empty ContentText."""
        content = ContentText.empty()
        
        assert content.value == ""
        assert content.is_empty() is True

    def test_is_empty_with_empty_string(self) -> None:
        """Test is_empty with empty string."""
        content = ContentText("")
        
        assert content.is_empty() is True

    def test_is_empty_with_whitespace_only(self) -> None:
        """Test is_empty with whitespace-only content."""
        content = ContentText("   \n\t  ")
        
        assert content.is_empty() is True

    def test_is_empty_with_content(self) -> None:
        """Test is_empty with actual content."""
        content = ContentText("Hello")
        
        assert content.is_empty() is False

    def test_length(self) -> None:
        """Test length method."""
        content = ContentText("Hello world")
        
        assert content.length() == 11
        assert len(content) == 11  # Test __len__ method

    def test_stripped(self) -> None:
        """Test stripped method returns new ContentText with trimmed whitespace."""
        content = ContentText("  Hello world  ")
        stripped = content.stripped()
        
        assert stripped.value == "Hello world"
        assert content.value == "  Hello world  "  # Original unchanged

    def test_truncated_shorter_than_limit(self) -> None:
        """Test truncated when content is shorter than limit."""
        content = ContentText("Short")
        truncated = content.truncated(10)
        
        assert truncated.value == "Short"

    def test_truncated_longer_than_limit(self) -> None:
        """Test truncated when content is longer than limit."""
        content = ContentText("This is a very long content string")
        truncated = content.truncated(10)
        
        assert truncated.value == "This is..."
        assert len(truncated.value) == 10

    def test_truncated_with_custom_suffix(self) -> None:
        """Test truncated with custom suffix."""
        content = ContentText("Long content")
        truncated = content.truncated(8, suffix=">>")
        
        assert truncated.value == "Long c>>"
        assert len(truncated.value) == 8

    def test_truncated_suffix_longer_than_limit(self) -> None:
        """Test truncated when suffix is longer than limit."""
        content = ContentText("Content")
        truncated = content.truncated(2, suffix="...")
        
        assert truncated.value == ".."
        assert len(truncated.value) == 2

    def test_contains_text_case_sensitive(self) -> None:
        """Test contains_text with case sensitive search."""
        content = ContentText("Hello World")
        
        assert content.contains_text("Hello", case_sensitive=True) is True
        assert content.contains_text("hello", case_sensitive=True) is False
        assert content.contains_text("World", case_sensitive=True) is True

    def test_contains_text_case_insensitive(self) -> None:
        """Test contains_text with case insensitive search (default)."""
        content = ContentText("Hello World")
        
        assert content.contains_text("hello") is True
        assert content.contains_text("WORLD") is True
        assert content.contains_text("xyz") is False

    def test_string_representation(self) -> None:
        """Test string representation of ContentText."""
        content = ContentText("Test content")
        
        assert str(content) == "Test content"

    def test_repr_representation_short_content(self) -> None:
        """Test repr representation with short content."""
        content = ContentText("Short")
        
        assert repr(content) == "ContentText('Short')"

    def test_repr_representation_long_content(self) -> None:
        """Test repr representation with long content (should be truncated)."""
        long_text = "This is a very long content that should be truncated in repr"
        content = ContentText(long_text)
        
        repr_str = repr(content)
        assert repr_str.startswith("ContentText('")
        assert len(repr_str) <= 65  # Should be truncated to ~50 chars + formatting

    def test_immutability(self) -> None:
        """Test that ContentText is immutable (frozen dataclass)."""
        content = ContentText("Test")
        
        with pytest.raises(Exception):  # dataclass.FrozenInstanceError in Python 3.7+
            content.value = "Changed"  # type: ignore

    def test_type_validation_in_post_init(self) -> None:
        """Test that __post_init__ validates the string type."""
        with pytest.raises(TypeError, match="ContentText must be a string"):
            ContentText(123)  # type: ignore

    def test_no_length_restrictions(self) -> None:
        """Test that ContentText accepts very long content (no length limits)."""
        very_long_content = "A" * 10000  # 10k characters
        content = ContentText(very_long_content)
        
        assert content.value == very_long_content
        assert content.length() == 10000

    def test_supports_unicode(self) -> None:
        """Test that ContentText supports Unicode characters."""
        unicode_content = "Hello 🌍 世界 🚀"
        content = ContentText(unicode_content)
        
        assert content.value == unicode_content
        assert content.contains_text("🌍") is True

    def test_supports_multiline_content(self) -> None:
        """Test that ContentText supports multiline content."""
        multiline_content = "Line 1\nLine 2\nLine 3"
        content = ContentText(multiline_content)
        
        assert content.value == multiline_content
        assert content.contains_text("Line 2") is True