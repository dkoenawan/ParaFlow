"""ResourceTags value object for validated resource tagging system."""

import re
from dataclasses import dataclass
from typing import Set, List, Iterator


@dataclass(frozen=True)
class ResourceTags:
    """Value object representing a validated set of resource tags.
    
    Provides validation, normalization, and operations for resource tags.
    Tags are normalized to lowercase and validated for format.
    """
    
    tags: frozenset[str]

    def __post_init__(self) -> None:
        """Validate the tags after initialization."""
        if not isinstance(self.tags, frozenset):
            raise TypeError(f"Tags must be a frozenset, got {type(self.tags)}")
        
        # Validate each tag
        for tag in self.tags:
            if not isinstance(tag, str):
                raise TypeError(f"All tags must be strings, got {type(tag)}")
            if not self._is_valid_tag(tag):
                raise ValueError(f"Invalid tag format: '{tag}'. Tags must be non-empty, alphanumeric with hyphens/underscores only")

    @classmethod
    def create(cls, tags: List[str] | Set[str] | None = None) -> "ResourceTags":
        """Create ResourceTags from a list or set of tag strings.
        
        Args:
            tags: List or set of tag strings (None creates empty tags)
            
        Returns:
            ResourceTags object with normalized tags
            
        Raises:
            TypeError: If tags is not a list, set, or None
            ValueError: If any tag has invalid format
        """
        if tags is None:
            return cls(frozenset())
        
        if not isinstance(tags, (list, set, frozenset)):
            raise TypeError(f"Tags must be a list, set, or None, got {type(tags)}")
        
        # Normalize tags: strip whitespace, convert to lowercase, remove duplicates
        normalized_tags = set()
        for tag in tags:
            if not isinstance(tag, str):
                raise TypeError(f"All tags must be strings, got {type(tag)}")
            
            normalized_tag = cls._normalize_tag(tag)
            if normalized_tag:  # Skip empty tags after normalization
                normalized_tags.add(normalized_tag)
        
        return cls(frozenset(normalized_tags))

    @classmethod
    def empty(cls) -> "ResourceTags":
        """Create empty ResourceTags.
        
        Returns:
            ResourceTags with no tags
        """
        return cls(frozenset())

    @classmethod
    def from_string(cls, tags_string: str, separator: str = ",") -> "ResourceTags":
        """Create ResourceTags from a delimited string.
        
        Args:
            tags_string: String containing tags separated by separator
            separator: Character used to separate tags (default: comma)
            
        Returns:
            ResourceTags object
            
        Example:
            ResourceTags.from_string("work,productivity,notes") -> ResourceTags with 3 tags
        """
        if not tags_string.strip():
            return cls.empty()
        
        tag_list = [tag.strip() for tag in tags_string.split(separator)]
        return cls.create(tag_list)

    def add(self, tag: str) -> "ResourceTags":
        """Add a tag and return a new ResourceTags instance.
        
        Args:
            tag: Tag string to add
            
        Returns:
            New ResourceTags with the added tag
            
        Raises:
            ValueError: If tag format is invalid
        """
        normalized_tag = self._normalize_tag(tag)
        if not normalized_tag:
            return self  # Skip empty tags
        
        new_tags = set(self.tags)
        new_tags.add(normalized_tag)
        return ResourceTags(frozenset(new_tags))

    def remove(self, tag: str) -> "ResourceTags":
        """Remove a tag and return a new ResourceTags instance.
        
        Args:
            tag: Tag string to remove
            
        Returns:
            New ResourceTags without the specified tag
        """
        normalized_tag = self._normalize_tag(tag)
        new_tags = set(self.tags)
        new_tags.discard(normalized_tag)  # discard doesn't raise if not found
        return ResourceTags(frozenset(new_tags))

    def union(self, other: "ResourceTags") -> "ResourceTags":
        """Combine with another ResourceTags instance.
        
        Args:
            other: Another ResourceTags instance
            
        Returns:
            New ResourceTags with combined tags
        """
        if not isinstance(other, ResourceTags):
            raise TypeError(f"Can only union with ResourceTags, got {type(other)}")
        
        combined_tags = self.tags.union(other.tags)
        return ResourceTags(combined_tags)

    def contains(self, tag: str) -> bool:
        """Check if a tag exists in the collection.
        
        Args:
            tag: Tag string to check
            
        Returns:
            True if tag exists (case-insensitive)
        """
        normalized_tag = self._normalize_tag(tag)
        return normalized_tag in self.tags

    def is_empty(self) -> bool:
        """Check if there are no tags.
        
        Returns:
            True if no tags are present
        """
        return len(self.tags) == 0

    def count(self) -> int:
        """Get the number of tags.
        
        Returns:
            Number of tags
        """
        return len(self.tags)

    def to_list(self) -> List[str]:
        """Convert tags to a sorted list.
        
        Returns:
            Sorted list of tag strings
        """
        return sorted(list(self.tags))

    def to_string(self, separator: str = ", ") -> str:
        """Convert tags to a delimited string.
        
        Args:
            separator: String to use between tags
            
        Returns:
            String representation of tags
        """
        return separator.join(self.to_list())

    @staticmethod
    def _normalize_tag(tag: str) -> str:
        """Normalize a tag string.
        
        Args:
            tag: Raw tag string
            
        Returns:
            Normalized tag string (lowercase, stripped)
        """
        return tag.strip().lower()

    @staticmethod
    def _is_valid_tag(tag: str) -> bool:
        """Check if a tag has valid format.
        
        Args:
            tag: Tag string to validate
            
        Returns:
            True if tag format is valid
        """
        if not tag or not tag.strip():
            return False
        
        # Allow alphanumeric characters, hyphens, and underscores
        # Must start and end with alphanumeric
        pattern = r'^[a-z0-9][a-z0-9_-]*[a-z0-9]$|^[a-z0-9]$'
        return bool(re.match(pattern, tag))

    def __iter__(self) -> Iterator[str]:
        """Allow iteration over tags."""
        return iter(sorted(self.tags))

    def __contains__(self, tag: str) -> bool:
        """Support 'in' operator for tag checking."""
        return self.contains(tag)

    def __len__(self) -> int:
        """Return the number of tags."""
        return len(self.tags)

    def __str__(self) -> str:
        """Return string representation of tags."""
        return self.to_string()

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        tag_list = self.to_list()
        if len(tag_list) <= 3:
            return f"ResourceTags({tag_list})"
        else:
            preview = tag_list[:3]
            return f"ResourceTags({preview}... +{len(tag_list)-3} more)"