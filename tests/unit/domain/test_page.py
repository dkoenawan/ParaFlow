"""
Unit tests for Page domain model.

This module tests the Page domain entity to ensure it behaves correctly
according to business rules and maintains data integrity.
"""

import pytest
from datetime import datetime
from packages.domain.models.page import Page


class TestPage:
    """Test cases for the Page domain model."""
    
    def test_page_creation_with_minimal_data(self):
        """Test creating a page with minimal required data."""
        page = Page(title="Test Page")
        
        assert page.title == "Test Page"
        assert page.content == ""
        assert page.id is None
        assert page.created_at is None
        assert page.updated_at is None
        assert page.metadata == {}
    
    def test_page_creation_with_full_data(self):
        """Test creating a page with all fields populated."""
        created_at = datetime.now()
        updated_at = datetime.now()
        metadata = {"source": "test", "category": "demo"}
        
        page = Page(
            id="test-id",
            title="Full Test Page",
            content="This is test content",
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata
        )
        
        assert page.id == "test-id"
        assert page.title == "Full Test Page"
        assert page.content == "This is test content"
        assert page.created_at == created_at
        assert page.updated_at == updated_at
        assert page.metadata == metadata
    
    def test_page_creation_with_none_metadata(self):
        """Test that None metadata is converted to empty dict."""
        page = Page(title="Test", metadata=None)
        
        assert page.metadata == {}
    
    def test_page_is_empty_with_no_content(self):
        """Test is_empty returns True when page has no title or content."""
        page = Page()
        assert page.is_empty() is True
        
        page = Page(title="", content="")
        assert page.is_empty() is True
        
        page = Page(title="   ", content="   ")
        assert page.is_empty() is True
    
    def test_page_is_empty_with_title_only(self):
        """Test is_empty returns False when page has title."""
        page = Page(title="Test Title")
        assert page.is_empty() is False
    
    def test_page_is_empty_with_content_only(self):
        """Test is_empty returns False when page has content."""
        page = Page(content="Test content")
        assert page.is_empty() is False
    
    def test_page_is_empty_with_both_title_and_content(self):
        """Test is_empty returns False when page has both title and content."""
        page = Page(title="Test Title", content="Test content")
        assert page.is_empty() is False
    
    def test_page_has_id_with_no_id(self):
        """Test has_id returns False when page has no ID."""
        page = Page(title="Test")
        assert page.has_id() is False
        
        page = Page(title="Test", id="")
        assert page.has_id() is False
        
        page = Page(title="Test", id="   ")
        assert page.has_id() is False
    
    def test_page_has_id_with_valid_id(self):
        """Test has_id returns True when page has valid ID."""
        page = Page(title="Test", id="valid-id")
        assert page.has_id() is True
    
    def test_page_string_representation(self):
        """Test page string representation."""
        page = Page(id="test-id", title="Test Title", content="Some content")
        str_repr = str(page)
        
        assert "test-id" in str_repr
        assert "Test Title" in str_repr
        assert "content_length=" in str_repr
    
    def test_page_string_representation_long_title(self):
        """Test page string representation with long title."""
        long_title = "This is a very long title that should be truncated in the string representation"
        page = Page(id="test-id", title=long_title, content="Some content")
        str_repr = str(page)
        
        assert "test-id" in str_repr
        assert len(str_repr) < len(long_title) + 100  # Should be truncated
        assert "..." in str_repr
    
    def test_page_immutability(self):
        """Test that Page is immutable (frozen dataclass)."""
        page = Page(title="Test")
        
        with pytest.raises(AttributeError):
            page.title = "New Title"
    
    def test_page_equality(self):
        """Test page equality comparison."""
        page1 = Page(id="1", title="Test", content="Content")
        page2 = Page(id="1", title="Test", content="Content")
        page3 = Page(id="2", title="Test", content="Content")
        
        assert page1 == page2
        assert page1 != page3
    
    def test_page_with_special_characters(self):
        """Test page with special characters in title and content."""
        page = Page(
            title="Special chars: àáâãäåæçèéêë",
            content="Content with émojis: 🚀 💻 ✨"
        )
        
        assert "àáâãäåæçèéêë" in page.title
        assert "🚀 💻 ✨" in page.content
        assert not page.is_empty()
    
    def test_page_with_very_long_content(self):
        """Test page with very long content."""
        long_content = "x" * 10000
        page = Page(title="Test", content=long_content)
        
        assert len(page.content) == 10000
        assert not page.is_empty()


@pytest.fixture
def sample_page():
    """Fixture providing a sample page for testing."""
    return Page(
        id="sample-id",
        title="Sample Page",
        content="This is sample content for testing",
        created_at=datetime(2023, 1, 1),
        updated_at=datetime(2023, 1, 2),
        metadata={"category": "test", "priority": "high"}
    )


@pytest.fixture
def empty_page():
    """Fixture providing an empty page for testing."""
    return Page()


@pytest.fixture
def page_without_id():
    """Fixture providing a page without ID for testing creation scenarios."""
    return Page(
        title="New Page",
        content="Content for new page",
        metadata={"status": "draft"}
    )