"""Resource domain entity for PARA methodology organization."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .resource_id import ResourceId
from .content_text import ContentText
from .para_category import PARACategory
from .resource_tags import ResourceTags
from .thought_id import ThoughtId


@dataclass(frozen=True)
class Resource:
    """Domain entity representing a resource organized by PARA methodology.
    
    Resources are the output of processed thoughts, categorized into the PARA framework:
    Projects, Areas, Resources, and Archives. Immutable to ensure data integrity.
    
    Attributes:
        id: Unique identifier for the resource
        title: Brief title or summary of the resource
        content: Rich content of the resource
        category: PARA category (Project/Area/Resource/Archive)
        tags: Set of tags for flexible organization
        source_thought: Reference to the originating thought (if any)
        created_date: When the resource was created
        updated_date: When the resource was last modified
        deadline: Optional deadline for projects
    """
    
    id: ResourceId
    title: str
    content: ContentText
    category: PARACategory
    tags: ResourceTags
    source_thought: Optional[ThoughtId]
    created_date: datetime
    updated_date: datetime
    deadline: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate the resource after initialization."""
        # Validate title
        if not isinstance(self.title, str):
            raise TypeError("Title must be a string")
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
        
        # Validate content
        if not isinstance(self.content, ContentText):
            raise TypeError("Content must be a ContentText object")
        
        # Validate category
        if not isinstance(self.category, PARACategory):
            raise TypeError("Category must be a PARACategory enum")
        
        # Validate tags
        if not isinstance(self.tags, ResourceTags):
            raise TypeError("Tags must be a ResourceTags object")
        
        # Validate source_thought
        if self.source_thought is not None and not isinstance(self.source_thought, ThoughtId):
            raise TypeError("Source thought must be a ThoughtId or None")
        
        # Validate dates
        if not isinstance(self.created_date, datetime):
            raise TypeError("Created date must be a datetime object")
        if not isinstance(self.updated_date, datetime):
            raise TypeError("Updated date must be a datetime object")
        
        # Validate deadline
        if self.deadline is not None and not isinstance(self.deadline, datetime):
            raise TypeError("Deadline must be a datetime object or None")
        
        # Business rule validations
        self._validate_business_rules()

    def _validate_business_rules(self) -> None:
        """Validate PARA methodology business rules."""
        # Projects should typically have deadlines (warning, not error)
        if self.category == PARACategory.PROJECT and self.deadline is None:
            # This could be logged as a warning in a real system
            pass
        
        # Archives shouldn't have future deadlines
        if self.category == PARACategory.ARCHIVE and self.deadline is not None:
            if self.deadline > datetime.utcnow():
                raise ValueError("Archived resources cannot have future deadlines")
        
        # Updated date should not be before created date
        if self.updated_date < self.created_date:
            raise ValueError("Updated date cannot be before created date")

    @classmethod
    def create_new(
        cls,
        title: str,
        content: str,
        category: PARACategory,
        tags: list[str] | None = None,
        source_thought: ThoughtId | None = None,
        deadline: datetime | None = None,
        created_date: datetime | None = None,
    ) -> "Resource":
        """Create a new resource with generated ID and default values.
        
        Args:
            title: Brief title or summary of the resource
            content: Rich content of the resource
            category: PARA category for the resource
            tags: Optional list of tags for organization
            source_thought: Optional reference to originating thought
            deadline: Optional deadline (typically for projects)
            created_date: Creation timestamp (defaults to now)
            
        Returns:
            New Resource entity
            
        Raises:
            ValueError: If title is empty or business rules are violated
            TypeError: If parameters have wrong types
        """
        now = created_date or datetime.utcnow()
        
        return cls(
            id=ResourceId.generate(),
            title=title,
            content=ContentText.create(content),
            category=category,
            tags=ResourceTags.create(tags),
            source_thought=source_thought,
            created_date=now,
            updated_date=now,
            deadline=deadline,
        )

    @classmethod
    def restore(
        cls,
        id_value: str,
        title: str,
        content: str,
        category: str,
        tags: list[str],
        source_thought_id: str | None,
        created_date: datetime,
        updated_date: datetime,
        deadline: datetime | None = None,
    ) -> "Resource":
        """Restore a resource from persistent storage.
        
        Args:
            id_value: String representation of the resource ID
            title: Resource title
            content: Resource content
            category: PARA category string
            tags: List of tag strings
            source_thought_id: String representation of source thought ID
            created_date: Creation timestamp
            updated_date: Last update timestamp
            deadline: Optional deadline
            
        Returns:
            Restored Resource entity
            
        Raises:
            ValueError: If any values are invalid
        """
        source_thought = ThoughtId.from_string(source_thought_id) if source_thought_id else None
        
        return cls(
            id=ResourceId.from_string(id_value),
            title=title,
            content=ContentText.create(content),
            category=PARACategory.from_string(category),
            tags=ResourceTags.create(tags),
            source_thought=source_thought,
            created_date=created_date,
            updated_date=updated_date,
            deadline=deadline,
        )

    def update_content(self, new_content: str) -> "Resource":
        """Update the content and return a new Resource instance.
        
        Args:
            new_content: New content text
            
        Returns:
            New Resource with updated content and updated_date
        """
        return self._create_updated_copy(
            content=ContentText.create(new_content),
            updated_date=datetime.utcnow()
        )

    def update_category(self, new_category: PARACategory) -> "Resource":
        """Update the PARA category and return a new Resource instance.
        
        Args:
            new_category: New PARA category
            
        Returns:
            New Resource with updated category
            
        Raises:
            ValueError: If transition to new category is not allowed
        """
        if not self.category.can_transition_to(new_category):
            raise ValueError(
                f"Cannot transition from {self.category} to {new_category}. "
                f"Check PARA methodology transition rules."
            )
        
        return self._create_updated_copy(
            category=new_category,
            updated_date=datetime.utcnow()
        )

    def add_tag(self, tag: str) -> "Resource":
        """Add a tag and return a new Resource instance.
        
        Args:
            tag: Tag to add
            
        Returns:
            New Resource with added tag
        """
        return self._create_updated_copy(
            tags=self.tags.add(tag),
            updated_date=datetime.utcnow()
        )

    def remove_tag(self, tag: str) -> "Resource":
        """Remove a tag and return a new Resource instance.
        
        Args:
            tag: Tag to remove
            
        Returns:
            New Resource without the specified tag
        """
        return self._create_updated_copy(
            tags=self.tags.remove(tag),
            updated_date=datetime.utcnow()
        )

    def update_tags(self, new_tags: list[str]) -> "Resource":
        """Update all tags and return a new Resource instance.
        
        Args:
            new_tags: New list of tags
            
        Returns:
            New Resource with updated tags
        """
        return self._create_updated_copy(
            tags=ResourceTags.create(new_tags),
            updated_date=datetime.utcnow()
        )

    def set_deadline(self, deadline: datetime | None) -> "Resource":
        """Set or update the deadline and return a new Resource instance.
        
        Args:
            deadline: New deadline (None to remove)
            
        Returns:
            New Resource with updated deadline
            
        Raises:
            ValueError: If setting deadline violates business rules
        """
        # Validate business rules for deadline
        if self.category == PARACategory.ARCHIVE and deadline is not None:
            if deadline > datetime.utcnow():
                raise ValueError("Cannot set future deadline for archived resource")
        
        return self._create_updated_copy(
            deadline=deadline,
            updated_date=datetime.utcnow()
        )

    def archive(self) -> "Resource":
        """Archive the resource by changing category to ARCHIVE.
        
        Returns:
            New Resource with ARCHIVE category
        """
        return self._create_updated_copy(
            category=PARACategory.ARCHIVE,
            updated_date=datetime.utcnow()
        )

    def is_active(self) -> bool:
        """Check if the resource is in an active category.
        
        Returns:
            True if category is not ARCHIVE
        """
        return self.category.is_active()

    def is_overdue(self) -> bool:
        """Check if the resource is overdue (has deadline in the past).
        
        Returns:
            True if deadline exists and is in the past
        """
        if self.deadline is None:
            return False
        return self.deadline < datetime.utcnow()

    def days_until_deadline(self) -> int | None:
        """Calculate days until deadline.
        
        Returns:
            Number of days until deadline (negative if overdue), None if no deadline
        """
        if self.deadline is None:
            return None
        
        delta = self.deadline - datetime.utcnow()
        return delta.days

    def has_source_thought(self) -> bool:
        """Check if the resource originated from a thought.
        
        Returns:
            True if source_thought is not None
        """
        return self.source_thought is not None

    def get_content_preview(self, max_length: int = 100) -> str:
        """Get a preview of the content for display purposes.
        
        Args:
            max_length: Maximum length of the preview
            
        Returns:
            Truncated content string
        """
        return str(self.content.truncated(max_length))

    def _create_updated_copy(self, **kwargs) -> "Resource":
        """Create a new instance with updated fields.
        
        Args:
            **kwargs: Fields to update
            
        Returns:
            New Resource with updated fields
        """
        # Create a dictionary of current values
        current_values = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'tags': self.tags,
            'source_thought': self.source_thought,
            'created_date': self.created_date,
            'updated_date': self.updated_date,
            'deadline': self.deadline,
        }
        
        # Update with new values
        current_values.update(kwargs)
        
        return Resource(**current_values)

    def __str__(self) -> str:
        """Return string representation of the resource."""
        return f"Resource(id={self.id}, title='{self.title}', category={self.category})"

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"Resource("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"category={self.category}, "
            f"tags={len(self.tags)} tags, "
            f"active={self.is_active()}"
            f")"
        )