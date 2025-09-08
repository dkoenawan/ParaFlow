"""
Page domain model for PARA framework.

This module defines the core Page entity used throughout the application.
The Page model is technology-agnostic and represents the business concept
of a page that can contain content and metadata.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass(frozen=True)
class Page:
    """
    Domain entity representing a page in the PARA framework.
    
    This is a technology-agnostic representation of a page that can
    be stored in any data store (Notion, Excel, text files, etc.).
    """
    
    id: Optional[str] = None
    title: str = ""
    content: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize metadata dict if None to prevent mutable default argument."""
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
    
    def is_empty(self) -> bool:
        """Check if the page has no content."""
        return not self.title.strip() and not self.content.strip()
    
    def has_id(self) -> bool:
        """Check if the page has been persisted (has an ID)."""
        return self.id is not None and self.id.strip() != ""
    
    def __str__(self) -> str:
        """String representation of the page."""
        return f"Page(id={self.id}, title='{self.title[:50]}...', content_length={len(self.content)})"