"""ThoughtContent domain entity for thought streaming and processing."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .thought_id import ThoughtId
from .content_text import ContentText
from .processing_status import ProcessingStatus


@dataclass(frozen=True)
class ThoughtContent:
    """Domain entity representing a user's thought for processing.
    
    Supports free-form thought streaming with optional user tagging
    to minimize AI categorization errors. Immutable to ensure data integrity.
    
    Attributes:
        id: Unique identifier for the thought
        title: Brief title or summary of the thought
        content: Free-form thought content (no length limits)
        created_date: When the thought was created
        processed: Whether the thought has been processed
        processing_status: Current processing state
        project_tag: Optional user-assigned project tag (free text)
        area_tag: Optional user-assigned area tag (free text)
    """
    
    id: ThoughtId
    title: str
    content: ContentText
    created_date: datetime
    processed: bool
    processing_status: ProcessingStatus
    project_tag: Optional[str] = None
    area_tag: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate the thought content after initialization."""
        # Validate title
        if not isinstance(self.title, str):
            raise TypeError("Title must be a string")
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
        
        # Validate content
        if not isinstance(self.content, ContentText):
            raise TypeError("Content must be a ContentText object")
        
        # Validate created_date
        if not isinstance(self.created_date, datetime):
            raise TypeError("Created date must be a datetime object")
        
        # Validate processed flag
        if not isinstance(self.processed, bool):
            raise TypeError("Processed must be a boolean")
        
        # Validate processing_status
        if not isinstance(self.processing_status, ProcessingStatus):
            raise TypeError("Processing status must be a ProcessingStatus enum")
        
        # Validate optional tags
        if self.project_tag is not None and not isinstance(self.project_tag, str):
            raise TypeError("Project tag must be a string or None")
        if self.area_tag is not None and not isinstance(self.area_tag, str):
            raise TypeError("Area tag must be a string or None")

    @classmethod
    def create_new(
        cls,
        title: str,
        content: str,
        project_tag: Optional[str] = None,
        area_tag: Optional[str] = None,
        created_date: Optional[datetime] = None,
    ) -> "ThoughtContent":
        """Create a new thought with generated ID and default values.
        
        Args:
            title: Brief title or summary of the thought
            content: Free-form thought content
            project_tag: Optional user-assigned project tag
            area_tag: Optional user-assigned area tag
            created_date: Creation timestamp (defaults to now)
            
        Returns:
            New ThoughtContent entity
            
        Raises:
            ValueError: If title is empty
            TypeError: If parameters have wrong types
        """
        return cls(
            id=ThoughtId.generate(),
            title=title,
            content=ContentText.create(content),
            created_date=created_date or datetime.utcnow(),
            processed=False,
            processing_status=ProcessingStatus.PENDING,
            project_tag=project_tag,
            area_tag=area_tag,
        )

    @classmethod
    def restore(
        cls,
        id_value: str,
        title: str,
        content: str,
        created_date: datetime,
        processed: bool,
        processing_status: str,
        project_tag: Optional[str] = None,
        area_tag: Optional[str] = None,
    ) -> "ThoughtContent":
        """Restore a thought from persistent storage.
        
        Args:
            id_value: String representation of the thought ID
            title: Thought title
            content: Thought content
            created_date: Creation timestamp
            processed: Processing flag
            processing_status: Processing status string
            project_tag: Optional project tag
            area_tag: Optional area tag
            
        Returns:
            Restored ThoughtContent entity
            
        Raises:
            ValueError: If any values are invalid
        """
        return cls(
            id=ThoughtId.from_string(id_value),
            title=title,
            content=ContentText.create(content),
            created_date=created_date,
            processed=processed,
            processing_status=ProcessingStatus.from_string(processing_status),
            project_tag=project_tag,
            area_tag=area_tag,
        )

    def mark_as_processing(self) -> "ThoughtContent":
        """Mark the thought as currently being processed.
        
        Returns:
            New ThoughtContent with processing status updated
            
        Raises:
            ValueError: If current status cannot transition to PROCESSING
        """
        if not self.processing_status.can_transition_to(ProcessingStatus.PROCESSING):
            raise ValueError(
                f"Cannot transition from {self.processing_status} to PROCESSING"
            )
        
        return self._update_status(ProcessingStatus.PROCESSING)

    def mark_as_completed(self) -> "ThoughtContent":
        """Mark the thought as successfully processed.
        
        Returns:
            New ThoughtContent with completed status
            
        Raises:
            ValueError: If current status cannot transition to COMPLETED
        """
        if not self.processing_status.can_transition_to(ProcessingStatus.COMPLETED):
            raise ValueError(
                f"Cannot transition from {self.processing_status} to COMPLETED"
            )
        
        return self._update_status(ProcessingStatus.COMPLETED, processed=True)

    def mark_as_failed(self) -> "ThoughtContent":
        """Mark the thought processing as failed.
        
        Returns:
            New ThoughtContent with failed status
            
        Raises:
            ValueError: If current status cannot transition to FAILED
        """
        if not self.processing_status.can_transition_to(ProcessingStatus.FAILED):
            raise ValueError(
                f"Cannot transition from {self.processing_status} to FAILED"
            )
        
        return self._update_status(ProcessingStatus.FAILED)

    def mark_as_skipped(self) -> "ThoughtContent":
        """Mark the thought as skipped (duplicate or invalid).
        
        Returns:
            New ThoughtContent with skipped status
            
        Raises:
            ValueError: If current status cannot transition to SKIPPED
        """
        if not self.processing_status.can_transition_to(ProcessingStatus.SKIPPED):
            raise ValueError(
                f"Cannot transition from {self.processing_status} to SKIPPED"
            )
        
        return self._update_status(ProcessingStatus.SKIPPED, processed=True)

    def has_user_tags(self) -> bool:
        """Check if the thought has any user-assigned tags.
        
        Returns:
            True if either project_tag or area_tag is set
        """
        return bool(self.project_tag or self.area_tag)

    def get_content_preview(self, max_length: int = 100) -> str:
        """Get a preview of the content for display purposes.
        
        Args:
            max_length: Maximum length of the preview
            
        Returns:
            Truncated content string
        """
        return str(self.content.truncated(max_length))

    def _update_status(
        self, 
        new_status: ProcessingStatus, 
        processed: Optional[bool] = None
    ) -> "ThoughtContent":
        """Create a new instance with updated status.
        
        Args:
            new_status: New processing status
            processed: New processed flag (if provided)
            
        Returns:
            New ThoughtContent with updated status
        """
        return ThoughtContent(
            id=self.id,
            title=self.title,
            content=self.content,
            created_date=self.created_date,
            processed=processed if processed is not None else self.processed,
            processing_status=new_status,
            project_tag=self.project_tag,
            area_tag=self.area_tag,
        )

    def __str__(self) -> str:
        """Return string representation of the thought."""
        return f"ThoughtContent(id={self.id}, title='{self.title}')"

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"ThoughtContent("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"status={self.processing_status}, "
            f"processed={self.processed}"
            f")"
        )