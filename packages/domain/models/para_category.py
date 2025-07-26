"""PARA Category enumeration for organizing resources."""

from enum import Enum


class PARACategory(Enum):
    """Enumeration of PARA methodology categories for organizing resources.
    
    PARA is a productivity method that organizes information into four categories:
    - PROJECT: Things with a deadline and specific outcome
    - AREA: Ongoing responsibilities to maintain  
    - RESOURCE: Topics of ongoing interest
    - ARCHIVE: Inactive items from the other three categories
    """
    
    PROJECT = "project"
    AREA = "area"
    RESOURCE = "resource"
    ARCHIVE = "archive"

    def __str__(self) -> str:
        """Return the string representation of the category."""
        return self.value

    @classmethod
    def from_string(cls, category: str) -> "PARACategory":
        """Create PARACategory from string value.
        
        Args:
            category: String representation of the category
            
        Returns:
            PARACategory enum value
            
        Raises:
            ValueError: If category string is not valid
        """
        try:
            return cls(category.lower())
        except ValueError:
            valid_categories = [c.value for c in cls]
            raise ValueError(
                f"Invalid PARA category: {category}. "
                f"Valid categories are: {', '.join(valid_categories)}"
            )

    def can_transition_to(self, new_category: "PARACategory") -> bool:
        """Check if this category can transition to another category.
        
        Valid transitions follow PARA methodology principles:
        - PROJECT -> ARCHIVE (when completed)
        - PROJECT -> AREA (when it becomes ongoing)
        - AREA -> ARCHIVE (when no longer active)
        - RESOURCE -> ARCHIVE (when no longer relevant)
        - ARCHIVE -> PROJECT/AREA/RESOURCE (when reactivated)
        
        Args:
            new_category: The category to transition to
            
        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions = {
            PARACategory.PROJECT: {PARACategory.ARCHIVE, PARACategory.AREA},
            PARACategory.AREA: {PARACategory.ARCHIVE},
            PARACategory.RESOURCE: {PARACategory.ARCHIVE},
            PARACategory.ARCHIVE: {PARACategory.PROJECT, PARACategory.AREA, PARACategory.RESOURCE},
        }
        
        return new_category in valid_transitions.get(self, set())

    def get_description(self) -> str:
        """Get a human-readable description of the category.
        
        Returns:
            Description of what the category represents
        """
        descriptions = {
            PARACategory.PROJECT: "Things with a deadline and specific outcome",
            PARACategory.AREA: "Ongoing responsibilities to maintain",
            PARACategory.RESOURCE: "Topics of ongoing interest",
            PARACategory.ARCHIVE: "Inactive items from other categories",
        }
        return descriptions[self]

    def is_active(self) -> bool:
        """Check if this category represents active content.
        
        Returns:
            True if category is PROJECT, AREA, or RESOURCE; False if ARCHIVE
        """
        return self != PARACategory.ARCHIVE

    def requires_deadline(self) -> bool:
        """Check if this category typically requires a deadline.
        
        Returns:
            True if category is PROJECT (which should have deadlines)
        """
        return self == PARACategory.PROJECT

    def allows_indefinite_duration(self) -> bool:
        """Check if this category allows indefinite duration.
        
        Returns:
            True if category is AREA or RESOURCE (ongoing/reference)
        """
        return self in {PARACategory.AREA, PARACategory.RESOURCE}