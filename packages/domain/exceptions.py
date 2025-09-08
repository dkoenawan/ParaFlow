"""
Domain exceptions for PARA framework.

This module defines business-specific exceptions that can be raised
by domain services and use cases. These exceptions are technology-agnostic
and represent business rule violations or domain-level errors.
"""


class DomainError(Exception):
    """Base exception for all domain-related errors."""
    pass


class ValidationError(DomainError):
    """Raised when domain entity validation fails."""
    pass


class PageError(DomainError):
    """Base exception for page-related errors."""
    pass


class PageNotFoundError(PageError):
    """Raised when a requested page does not exist."""
    
    def __init__(self, page_id: str):
        super().__init__(f"Page with ID '{page_id}' not found")
        self.page_id = page_id


class PageCreationError(PageError):
    """Raised when page creation fails."""
    pass


class PageUpdateError(PageError):
    """Raised when page update operation fails."""
    pass


class PageDeletionError(PageError):
    """Raised when page deletion operation fails."""
    pass


class PageRetrievalError(PageError):
    """Raised when page retrieval operation fails."""
    pass