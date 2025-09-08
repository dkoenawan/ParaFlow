"""
Unit tests for page operations use cases.

This module tests the application-layer use cases to ensure they
properly orchestrate domain logic and handle business rules.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from packages.domain.models.page import Page
from packages.domain.ports.page_repository import PageRepositoryPort
from packages.domain.exceptions import ValidationError, PageNotFoundError
from packages.application.use_cases.page_operations import (
    CreatePageUseCase,
    GetPageUseCase,
    UpdatePageUseCase,
    DeletePageUseCase,
    ListPagesUseCase,
    PageApplicationService
)


class TestCreatePageUseCase:
    """Test cases for CreatePageUseCase."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock page repository for testing."""
        return AsyncMock(spec=PageRepositoryPort)
    
    @pytest.fixture
    def create_use_case(self, mock_repository):
        """CreatePageUseCase instance for testing."""
        return CreatePageUseCase(mock_repository)
    
    @pytest.mark.asyncio
    async def test_execute_success(self, create_use_case, mock_repository):
        """Test successful page creation."""
        # Arrange
        created_page = Page(id="123", title="Test Page", content="Test content")
        mock_repository.create_page.return_value = created_page
        
        # Act
        result = await create_use_case.execute("Test Page", "Test content")
        
        # Assert
        assert result == created_page
        mock_repository.create_page.assert_called_once()
        call_args = mock_repository.create_page.call_args[0][0]
        assert call_args.title == "Test Page"
        assert call_args.content == "Test content"
        assert call_args.id is None
    
    @pytest.mark.asyncio
    async def test_execute_with_empty_title_raises_validation_error(self, create_use_case):
        """Test that empty title raises ValidationError."""
        with pytest.raises(ValidationError, match="Page title cannot be empty"):
            await create_use_case.execute("", "Test content")
    
    @pytest.mark.asyncio
    async def test_execute_with_whitespace_title_raises_validation_error(self, create_use_case):
        """Test that whitespace-only title raises ValidationError."""
        with pytest.raises(ValidationError, match="Page title cannot be empty"):
            await create_use_case.execute("   ", "Test content")
    
    @pytest.mark.asyncio
    async def test_execute_strips_title_whitespace(self, create_use_case, mock_repository):
        """Test that title whitespace is stripped."""
        # Arrange
        created_page = Page(id="123", title="Test Page", content="Test content")
        mock_repository.create_page.return_value = created_page
        
        # Act
        await create_use_case.execute("  Test Page  ", "Test content")
        
        # Assert
        call_args = mock_repository.create_page.call_args[0][0]
        assert call_args.title == "Test Page"
    
    @pytest.mark.asyncio
    async def test_execute_with_metadata(self, create_use_case, mock_repository):
        """Test page creation with metadata."""
        # Arrange
        metadata = {"category": "test", "priority": "high"}
        created_page = Page(id="123", title="Test Page", content="Test content", metadata=metadata)
        mock_repository.create_page.return_value = created_page
        
        # Act
        result = await create_use_case.execute("Test Page", "Test content", metadata)
        
        # Assert
        assert result.metadata == metadata
        call_args = mock_repository.create_page.call_args[0][0]
        assert call_args.metadata == metadata


class TestGetPageUseCase:
    """Test cases for GetPageUseCase."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock page repository for testing."""
        return AsyncMock(spec=PageRepositoryPort)
    
    @pytest.fixture
    def get_use_case(self, mock_repository):
        """GetPageUseCase instance for testing."""
        return GetPageUseCase(mock_repository)
    
    @pytest.mark.asyncio
    async def test_execute_success(self, get_use_case, mock_repository):
        """Test successful page retrieval."""
        # Arrange
        page = Page(id="123", title="Test Page", content="Test content")
        mock_repository.get_page_by_id.return_value = page
        
        # Act
        result = await get_use_case.execute("123")
        
        # Assert
        assert result == page
        mock_repository.get_page_by_id.assert_called_once_with("123")
    
    @pytest.mark.asyncio
    async def test_execute_page_not_found_raises_error(self, get_use_case, mock_repository):
        """Test that non-existent page raises PageNotFoundError."""
        # Arrange
        mock_repository.get_page_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(PageNotFoundError, match="Page with ID '123' not found"):
            await get_use_case.execute("123")
    
    @pytest.mark.asyncio
    async def test_execute_empty_id_raises_validation_error(self, get_use_case):
        """Test that empty page ID raises ValidationError."""
        with pytest.raises(ValidationError, match="Page ID cannot be empty"):
            await get_use_case.execute("")
    
    @pytest.mark.asyncio
    async def test_execute_strips_id_whitespace(self, get_use_case, mock_repository):
        """Test that page ID whitespace is stripped."""
        # Arrange
        page = Page(id="123", title="Test Page", content="Test content")
        mock_repository.get_page_by_id.return_value = page
        
        # Act
        await get_use_case.execute("  123  ")
        
        # Assert
        mock_repository.get_page_by_id.assert_called_once_with("123")


class TestUpdatePageUseCase:
    """Test cases for UpdatePageUseCase."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock page repository for testing."""
        return AsyncMock(spec=PageRepositoryPort)
    
    @pytest.fixture
    def update_use_case(self, mock_repository):
        """UpdatePageUseCase instance for testing."""
        return UpdatePageUseCase(mock_repository)
    
    @pytest.fixture
    def existing_page(self):
        """Existing page for update testing."""
        return Page(
            id="123",
            title="Original Title",
            content="Original content",
            created_at=datetime(2023, 1, 1),
            metadata={"category": "original"}
        )
    
    @pytest.mark.asyncio
    async def test_execute_update_title(self, update_use_case, mock_repository, existing_page):
        """Test updating page title."""
        # Arrange
        mock_repository.get_page_by_id.return_value = existing_page
        updated_page = Page(id="123", title="New Title", content="Original content")
        mock_repository.update_page.return_value = updated_page
        
        # Act
        result = await update_use_case.execute("123", title="New Title")
        
        # Assert
        assert result.title == "New Title"
        mock_repository.update_page.assert_called_once()
        call_args = mock_repository.update_page.call_args[0][0]
        assert call_args.title == "New Title"
        assert call_args.content == "Original content"
    
    @pytest.mark.asyncio
    async def test_execute_update_content(self, update_use_case, mock_repository, existing_page):
        """Test updating page content."""
        # Arrange
        mock_repository.get_page_by_id.return_value = existing_page
        updated_page = Page(id="123", title="Original Title", content="New content")
        mock_repository.update_page.return_value = updated_page
        
        # Act
        result = await update_use_case.execute("123", content="New content")
        
        # Assert
        assert result.content == "New content"
        call_args = mock_repository.update_page.call_args[0][0]
        assert call_args.title == "Original Title"
        assert call_args.content == "New content"
    
    @pytest.mark.asyncio
    async def test_execute_page_not_found_raises_error(self, update_use_case, mock_repository):
        """Test that updating non-existent page raises PageNotFoundError."""
        # Arrange
        mock_repository.get_page_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(PageNotFoundError, match="Page with ID '123' not found"):
            await update_use_case.execute("123", title="New Title")
    
    @pytest.mark.asyncio
    async def test_execute_empty_updated_title_raises_validation_error(self, update_use_case, mock_repository, existing_page):
        """Test that empty updated title raises ValidationError."""
        # Arrange
        mock_repository.get_page_by_id.return_value = existing_page
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Page title cannot be empty"):
            await update_use_case.execute("123", title="")


class TestDeletePageUseCase:
    """Test cases for DeletePageUseCase."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock page repository for testing."""
        return AsyncMock(spec=PageRepositoryPort)
    
    @pytest.fixture
    def delete_use_case(self, mock_repository):
        """DeletePageUseCase instance for testing."""
        return DeletePageUseCase(mock_repository)
    
    @pytest.mark.asyncio
    async def test_execute_success(self, delete_use_case, mock_repository):
        """Test successful page deletion."""
        # Arrange
        mock_repository.delete_page.return_value = True
        
        # Act
        result = await delete_use_case.execute("123")
        
        # Assert
        assert result is True
        mock_repository.delete_page.assert_called_once_with("123")
    
    @pytest.mark.asyncio
    async def test_execute_page_not_found(self, delete_use_case, mock_repository):
        """Test deleting non-existent page returns False."""
        # Arrange
        mock_repository.delete_page.return_value = False
        
        # Act
        result = await delete_use_case.execute("123")
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_execute_empty_id_raises_validation_error(self, delete_use_case):
        """Test that empty page ID raises ValidationError."""
        with pytest.raises(ValidationError, match="Page ID cannot be empty"):
            await delete_use_case.execute("")


class TestListPagesUseCase:
    """Test cases for ListPagesUseCase."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock page repository for testing."""
        return AsyncMock(spec=PageRepositoryPort)
    
    @pytest.fixture
    def list_use_case(self, mock_repository):
        """ListPagesUseCase instance for testing."""
        return ListPagesUseCase(mock_repository)
    
    @pytest.mark.asyncio
    async def test_execute_success(self, list_use_case, mock_repository):
        """Test successful page listing."""
        # Arrange
        pages = [
            Page(id="1", title="Page 1"),
            Page(id="2", title="Page 2")
        ]
        mock_repository.list_pages.return_value = pages
        
        # Act
        result = await list_use_case.execute()
        
        # Assert
        assert result == pages
        mock_repository.list_pages.assert_called_once_with(limit=None, offset=0)
    
    @pytest.mark.asyncio
    async def test_execute_with_pagination(self, list_use_case, mock_repository):
        """Test page listing with pagination parameters."""
        # Arrange
        pages = [Page(id="1", title="Page 1")]
        mock_repository.list_pages.return_value = pages
        
        # Act
        result = await list_use_case.execute(limit=10, offset=5)
        
        # Assert
        assert result == pages
        mock_repository.list_pages.assert_called_once_with(limit=10, offset=5)
    
    @pytest.mark.asyncio
    async def test_execute_invalid_limit_raises_validation_error(self, list_use_case):
        """Test that invalid limit raises ValidationError."""
        with pytest.raises(ValidationError, match="Limit must be greater than 0"):
            await list_use_case.execute(limit=0)
    
    @pytest.mark.asyncio
    async def test_execute_negative_offset_raises_validation_error(self, list_use_case):
        """Test that negative offset raises ValidationError."""
        with pytest.raises(ValidationError, match="Offset cannot be negative"):
            await list_use_case.execute(offset=-1)


class TestPageApplicationService:
    """Test cases for PageApplicationService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock page repository for testing."""
        return AsyncMock(spec=PageRepositoryPort)
    
    @pytest.fixture
    def app_service(self, mock_repository):
        """PageApplicationService instance for testing."""
        return PageApplicationService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_create_page_delegates_to_use_case(self, app_service, mock_repository):
        """Test that create_page delegates to CreatePageUseCase."""
        # Arrange
        created_page = Page(id="123", title="Test Page", content="Test content")
        mock_repository.create_page.return_value = created_page
        
        # Act
        result = await app_service.create_page("Test Page", "Test content")
        
        # Assert
        assert result == created_page
        mock_repository.create_page.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_page_exists_true(self, app_service, mock_repository):
        """Test page_exists returns True when page exists."""
        # Arrange
        page = Page(id="123", title="Test Page")
        mock_repository.get_page_by_id.return_value = page
        
        # Act
        result = await app_service.page_exists("123")
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_page_exists_false(self, app_service, mock_repository):
        """Test page_exists returns False when page does not exist."""
        # Arrange
        mock_repository.get_page_by_id.return_value = None
        
        # Act
        result = await app_service.page_exists("123")
        
        # Assert
        assert result is False