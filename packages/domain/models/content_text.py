"""ContentText value object for validated thought content."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ContentText:
    """Value object representing validated thought content text.
    
    Provides basic validation while maintaining the free-form nature
    of thought streaming. No length limits to support seamless flow.
    """
    
    value: str

    def __post_init__(self) -> None:
        """Validate the content text after initialization."""
        if not isinstance(self.value, str):
            raise TypeError(f"ContentText must be a string, got {type(self.value)}")

    @classmethod
    def create(cls, content: str) -> "ContentText":
        """Create a ContentText from a string.
        
        Args:
            content: The content text string
            
        Returns:
            ContentText object
            
        Raises:
            TypeError: If content is not a string
        """
        return cls(content)

    @classmethod
    def empty(cls) -> "ContentText":
        """Create an empty ContentText.
        
        Returns:
            ContentText with empty string value
        """
        return cls("")

    def is_empty(self) -> bool:
        """Check if the content is empty or only whitespace.
        
        Returns:
            True if content is empty or only whitespace
        """
        return not self.value.strip()

    def length(self) -> int:
        """Get the length of the content.
        
        Returns:
            Number of characters in the content
        """
        return len(self.value)

    def stripped(self) -> "ContentText":
        """Get a new ContentText with leading/trailing whitespace removed.
        
        Returns:
            New ContentText with stripped content
        """
        return ContentText(self.value.strip())

    def truncated(self, max_length: int, suffix: str = "...") -> "ContentText":
        """Get a truncated version of the content.
        
        Note: This is for display purposes only. The original content
        should remain unlimited for thought streaming.
        
        Args:
            max_length: Maximum length of the truncated content
            suffix: Suffix to append if content is truncated
            
        Returns:
            New ContentText with truncated content
        """
        if len(self.value) <= max_length:
            return self
        
        truncated_length = max_length - len(suffix)
        if truncated_length <= 0:
            return ContentText(suffix[:max_length])
        
        return ContentText(self.value[:truncated_length] + suffix)

    def contains_text(self, search_text: str, case_sensitive: bool = False) -> bool:
        """Check if the content contains specific text.
        
        Args:
            search_text: Text to search for
            case_sensitive: Whether the search should be case sensitive
            
        Returns:
            True if the content contains the search text
        """
        content = self.value if case_sensitive else self.value.lower()
        search = search_text if case_sensitive else search_text.lower()
        return search in content

    def __str__(self) -> str:
        """Return the string representation of the content."""
        return self.value

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        truncated = self.truncated(50).value
        return f"ContentText('{truncated}')"

    def __len__(self) -> int:
        """Return the length of the content."""
        return len(self.value)