"""
Page operations use cases.

This module contains the application-layer use cases for managing pages.
Use cases orchestrate domain logic and coordinate with infrastructure adapters
through the defined ports.
"""

from typing import List, Optional
from datetime import datetime

from ...domain.models.page import Page
from ...domain.ports.page_repository import PageRepositoryPort
from ...domain.exceptions import ValidationError, PageNotFoundError


class CreatePageUseCase:
    """
    Use case for creating a new page.
    
    This use case orchestrates the page creation process, including
    validation and persistence through the repository port.
    """
    
    def __init__(self, page_repository: PageRepositoryPort):
        """
        Initialize the use case.
        
        Args:
            page_repository: Repository port for page persistence
        """
        self.page_repository = page_repository
    
    async def execute(self, title: str, content: str = "", metadata: Optional[dict] = None) -> Page:
        """
        Execute the page creation use case.
        
        Args:
            title: Page title
            content: Page content
            metadata: Additional page metadata
            
        Returns:
            Created page with assigned ID
            
        Raises:
            ValidationError: If page data is invalid
            PageCreationError: If creation fails
        """
        # Validate input
        if not title.strip():
            raise ValidationError("Page title cannot be empty")
        
        # Create page entity
        page = Page(
            title=title.strip(),
            content=content,
            metadata=metadata or {}
        )
        
        # Persist through repository
        return await self.page_repository.create_page(page)


class GetPageUseCase:
    """
    Use case for retrieving a page by ID.
    
    This use case handles page retrieval with proper error handling
    for non-existent pages.
    """
    
    def __init__(self, page_repository: PageRepositoryPort):
        """
        Initialize the use case.
        
        Args:
            page_repository: Repository port for page retrieval
        """
        self.page_repository = page_repository
    
    async def execute(self, page_id: str) -> Page:
        """
        Execute the page retrieval use case.
        
        Args:
            page_id: Unique identifier of the page
            
        Returns:
            Retrieved page entity
            
        Raises:
            PageNotFoundError: If page does not exist
            PageRetrievalError: If retrieval fails
        """
        if not page_id.strip():
            raise ValidationError("Page ID cannot be empty")
        
        page = await self.page_repository.get_page_by_id(page_id.strip())
        if page is None:
            raise PageNotFoundError(page_id)
        
        return page


class UpdatePageUseCase:
    """
    Use case for updating an existing page.
    
    This use case handles page updates with validation and
    ensures the page exists before attempting updates.
    """
    
    def __init__(self, page_repository: PageRepositoryPort):
        """
        Initialize the use case.
        
        Args:
            page_repository: Repository port for page persistence
        """
        self.page_repository = page_repository
    
    async def execute(self, page_id: str, title: Optional[str] = None, 
                     content: Optional[str] = None, metadata: Optional[dict] = None) -> Page:
        """
        Execute the page update use case.
        
        Args:
            page_id: Unique identifier of the page to update
            title: New page title (if provided)
            content: New page content (if provided)
            metadata: New page metadata (if provided)
            
        Returns:
            Updated page entity
            
        Raises:
            PageNotFoundError: If page does not exist
            ValidationError: If update data is invalid
            PageUpdateError: If update fails
        """
        if not page_id.strip():
            raise ValidationError("Page ID cannot be empty")
        
        # Get existing page
        existing_page = await self.page_repository.get_page_by_id(page_id.strip())
        if existing_page is None:
            raise PageNotFoundError(page_id)
        
        # Build updated page entity
        updated_title = title.strip() if title is not None else existing_page.title
        updated_content = content if content is not None else existing_page.content
        updated_metadata = metadata if metadata is not None else existing_page.metadata
        
        # Validate updated data
        if not updated_title.strip():
            raise ValidationError("Page title cannot be empty")
        
        updated_page = Page(
            id=existing_page.id,
            title=updated_title,
            content=updated_content,
            created_at=existing_page.created_at,
            updated_at=datetime.now(),
            metadata=updated_metadata
        )
        
        # Persist changes
        return await self.page_repository.update_page(updated_page)


class DeletePageUseCase:
    """
    Use case for deleting a page.
    
    This use case handles page deletion with proper validation
    and confirmation of successful deletion.
    """
    
    def __init__(self, page_repository: PageRepositoryPort):
        """
        Initialize the use case.
        
        Args:
            page_repository: Repository port for page persistence
        """
        self.page_repository = page_repository
    
    async def execute(self, page_id: str) -> bool:
        """
        Execute the page deletion use case.
        
        Args:
            page_id: Unique identifier of the page to delete
            
        Returns:
            True if page was deleted, False if page did not exist
            
        Raises:
            ValidationError: If page ID is invalid
            PageDeletionError: If deletion fails
        """
        if not page_id.strip():
            raise ValidationError("Page ID cannot be empty")
        
        return await self.page_repository.delete_page(page_id.strip())


class ListPagesUseCase:
    """
    Use case for listing pages with optional pagination.
    
    This use case provides a way to retrieve multiple pages
    with optional filtering and pagination.
    """
    
    def __init__(self, page_repository: PageRepositoryPort):
        """
        Initialize the use case.
        
        Args:
            page_repository: Repository port for page retrieval
        """
        self.page_repository = page_repository
    
    async def execute(self, limit: Optional[int] = None, offset: int = 0) -> List[Page]:
        """
        Execute the list pages use case.
        
        Args:
            limit: Maximum number of pages to return
            offset: Number of pages to skip
            
        Returns:
            List of page entities
            
        Raises:
            ValidationError: If pagination parameters are invalid
            PageRetrievalError: If listing fails
        """
        if limit is not None and limit <= 0:
            raise ValidationError("Limit must be greater than 0")
        
        if offset < 0:
            raise ValidationError("Offset cannot be negative")
        
        return await self.page_repository.list_pages(limit=limit, offset=offset)


class PageApplicationService:
    """
    Application service that coordinates page operations.
    
    This service provides a higher-level interface that combines
    multiple use cases and handles common workflows.
    """
    
    def __init__(self, page_repository: PageRepositoryPort):
        """
        Initialize the application service.
        
        Args:
            page_repository: Repository port for page operations
        """
        self.create_use_case = CreatePageUseCase(page_repository)
        self.get_use_case = GetPageUseCase(page_repository)
        self.update_use_case = UpdatePageUseCase(page_repository)
        self.delete_use_case = DeletePageUseCase(page_repository)
        self.list_use_case = ListPagesUseCase(page_repository)
    
    async def create_page(self, title: str, content: str = "", metadata: Optional[dict] = None) -> Page:
        """Create a new page."""
        return await self.create_use_case.execute(title, content, metadata)
    
    async def get_page(self, page_id: str) -> Page:
        """Get a page by ID."""
        return await self.get_use_case.execute(page_id)
    
    async def update_page(self, page_id: str, title: Optional[str] = None,
                         content: Optional[str] = None, metadata: Optional[dict] = None) -> Page:
        """Update an existing page."""
        return await self.update_use_case.execute(page_id, title, content, metadata)
    
    async def delete_page(self, page_id: str) -> bool:
        """Delete a page."""
        return await self.delete_use_case.execute(page_id)
    
    async def list_pages(self, limit: Optional[int] = None, offset: int = 0) -> List[Page]:
        """List pages with optional pagination."""
        return await self.list_use_case.execute(limit, offset)
    
    async def page_exists(self, page_id: str) -> bool:
        """Check if a page exists."""
        try:
            await self.get_page(page_id)
            return True
        except PageNotFoundError:
            return False