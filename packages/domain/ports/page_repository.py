"""
Page repository port interface.

This module defines the abstract interface that must be implemented by
any technology-specific adapter (Notion, Excel, etc.) to provide
page storage functionality.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.page import Page


class PageRepositoryPort(ABC):
    """
    Abstract port interface for page repository operations.
    
    This interface defines the contract that must be implemented by
    any storage adapter (Notion, file system, database, etc.).
    It follows the hexagonal architecture pattern by defining the
    business requirements without specifying implementation details.
    """
    
    @abstractmethod
    async def create_page(self, page: Page) -> Page:
        """
        Create a new page in the storage system.
        
        Args:
            page: Page entity to create (without ID)
            
        Returns:
            Created page with assigned ID
            
        Raises:
            PageCreationError: If page creation fails
            ValidationError: If page data is invalid
        """
        raise NotImplementedError
    
    @abstractmethod
    async def get_page_by_id(self, page_id: str) -> Optional[Page]:
        """
        Retrieve a page by its unique identifier.
        
        Args:
            page_id: Unique identifier of the page
            
        Returns:
            Page entity if found, None otherwise
            
        Raises:
            PageRetrievalError: If retrieval operation fails
        """
        raise NotImplementedError
    
    @abstractmethod
    async def update_page(self, page: Page) -> Page:
        """
        Update an existing page in the storage system.
        
        Args:
            page: Page entity with updated data (must have ID)
            
        Returns:
            Updated page entity
            
        Raises:
            PageNotFoundError: If page does not exist
            PageUpdateError: If update operation fails
            ValidationError: If page data is invalid
        """
        raise NotImplementedError
    
    @abstractmethod
    async def delete_page(self, page_id: str) -> bool:
        """
        Delete a page from the storage system.
        
        Args:
            page_id: Unique identifier of the page to delete
            
        Returns:
            True if page was deleted, False if page did not exist
            
        Raises:
            PageDeletionError: If deletion operation fails
        """
        raise NotImplementedError
    
    @abstractmethod
    async def list_pages(self, limit: Optional[int] = None, offset: int = 0) -> List[Page]:
        """
        List pages with optional pagination.
        
        Args:
            limit: Maximum number of pages to return
            offset: Number of pages to skip
            
        Returns:
            List of page entities
            
        Raises:
            PageRetrievalError: If listing operation fails
        """
        raise NotImplementedError
    
    @abstractmethod
    async def page_exists(self, page_id: str) -> bool:
        """
        Check if a page exists in the storage system.
        
        Args:
            page_id: Unique identifier of the page
            
        Returns:
            True if page exists, False otherwise
            
        Raises:
            PageRetrievalError: If existence check fails
        """
        raise NotImplementedError