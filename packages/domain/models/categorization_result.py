"""Categorization result domain model for PARA methodology classification."""

from dataclasses import dataclass
from typing import Optional

from .para_category import PARACategory


@dataclass(frozen=True)
class CategorizationResult:
    """Domain model representing the result of PARA categorization analysis.
    
    Contains the categorization decision along with confidence metrics and
    supporting information to help users understand and validate the classification.
    
    Attributes:
        category: The assigned PARA category
        confidence: Confidence score from 0.0 (no confidence) to 1.0 (certain)
        reasoning: Human-readable explanation of the categorization decision
        suggested_tags: List of tags that might be relevant for organization
        requires_review: Whether this categorization should be reviewed by user
    """
    
    category: PARACategory
    confidence: float
    reasoning: str
    suggested_tags: list[str]
    requires_review: bool = False

    def __post_init__(self) -> None:
        """Validate the categorization result after initialization."""
        # Validate category
        if not isinstance(self.category, PARACategory):
            raise TypeError("Category must be a PARACategory enum")
        
        # Validate confidence
        if not isinstance(self.confidence, (int, float)):
            raise TypeError("Confidence must be a number")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        # Validate reasoning
        if not isinstance(self.reasoning, str):
            raise TypeError("Reasoning must be a string")
        if not self.reasoning.strip():
            raise ValueError("Reasoning cannot be empty")
        
        # Validate suggested_tags
        if not isinstance(self.suggested_tags, list):
            raise TypeError("Suggested tags must be a list")
        if not all(isinstance(tag, str) for tag in self.suggested_tags):
            raise TypeError("All suggested tags must be strings")
        
        # Validate requires_review
        if not isinstance(self.requires_review, bool):
            raise TypeError("Requires review must be a boolean")

    @classmethod
    def create_with_review(
        cls,
        category: PARACategory,
        confidence: float,
        reasoning: str,
        suggested_tags: Optional[list[str]] = None,
    ) -> "CategorizationResult":
        """Create a categorization result that requires user review.
        
        Args:
            category: The assigned PARA category
            confidence: Confidence score (0.0 to 1.0)
            reasoning: Explanation of the categorization decision
            suggested_tags: Optional list of suggested tags
            
        Returns:
            CategorizationResult with requires_review=True
        """
        return cls(
            category=category,
            confidence=confidence,
            reasoning=reasoning,
            suggested_tags=suggested_tags or [],
            requires_review=True,
        )

    @classmethod
    def create_confident(
        cls,
        category: PARACategory,
        reasoning: str,
        suggested_tags: Optional[list[str]] = None,
    ) -> "CategorizationResult":
        """Create a high-confidence categorization result.
        
        Args:
            category: The assigned PARA category
            reasoning: Explanation of the categorization decision
            suggested_tags: Optional list of suggested tags
            
        Returns:
            CategorizationResult with confidence=1.0 and requires_review=False
        """
        return cls(
            category=category,
            confidence=1.0,
            reasoning=reasoning,
            suggested_tags=suggested_tags or [],
            requires_review=False,
        )

    @classmethod
    def create_uncertain(
        cls,
        category: PARACategory,
        reasoning: str,
        suggested_tags: Optional[list[str]] = None,
    ) -> "CategorizationResult":
        """Create a low-confidence categorization result that requires review.
        
        Args:
            category: The assigned PARA category (likely fallback)
            reasoning: Explanation of why categorization is uncertain
            suggested_tags: Optional list of suggested tags
            
        Returns:
            CategorizationResult with low confidence and requires_review=True
        """
        return cls(
            category=category,
            confidence=0.3,
            reasoning=reasoning,
            suggested_tags=suggested_tags or [],
            requires_review=True,
        )

    def is_confident(self, threshold: float = 0.7) -> bool:
        """Check if the categorization confidence meets the threshold.
        
        Args:
            threshold: Minimum confidence level (default 0.7)
            
        Returns:
            True if confidence >= threshold
        """
        return self.confidence >= threshold

    def should_auto_categorize(self, confidence_threshold: float = 0.8) -> bool:
        """Check if this result is suitable for automatic categorization.
        
        Args:
            confidence_threshold: Minimum confidence for auto-categorization
            
        Returns:
            True if confidence is high enough and review is not required
        """
        return (
            self.confidence >= confidence_threshold 
            and not self.requires_review
        )

    def get_confidence_level(self) -> str:
        """Get a human-readable confidence level description.
        
        Returns:
            String describing the confidence level
        """
        if self.confidence >= 0.9:
            return "Very High"
        elif self.confidence >= 0.7:
            return "High"
        elif self.confidence >= 0.5:
            return "Medium"
        elif self.confidence >= 0.3:
            return "Low"
        else:
            return "Very Low"

    def to_dict(self) -> dict:
        """Convert to dictionary representation for serialization.
        
        Returns:
            Dictionary representation of the categorization result
        """
        return {
            "category": self.category.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "suggested_tags": self.suggested_tags,
            "requires_review": self.requires_review,
            "confidence_level": self.get_confidence_level(),
        }