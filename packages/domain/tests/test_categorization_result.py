"""Tests for CategorizationResult domain model."""

import pytest
from packages.domain.models.categorization_result import CategorizationResult
from packages.domain.models.para_category import PARACategory


class TestCategorizationResult:
    """Test cases for CategorizationResult domain model."""

    def test_valid_categorization_result_creation(self):
        """Test creating a valid categorization result."""
        result = CategorizationResult(
            category=PARACategory.PROJECT,
            confidence=0.85,
            reasoning="Clear project with deadline mentioned",
            suggested_tags=["work", "urgent"],
            requires_review=False
        )
        
        assert result.category == PARACategory.PROJECT
        assert result.confidence == 0.85
        assert result.reasoning == "Clear project with deadline mentioned"
        assert result.suggested_tags == ["work", "urgent"]
        assert result.requires_review is False

    def test_categorization_result_immutability(self):
        """Test that categorization result is immutable."""
        result = CategorizationResult(
            category=PARACategory.RESOURCE,
            confidence=0.7,
            reasoning="Reference material",
            suggested_tags=["learning"]
        )
        
        with pytest.raises(AttributeError):
            result.category = PARACategory.PROJECT

    def test_invalid_category_type(self):
        """Test validation of category type."""
        with pytest.raises(TypeError, match="Category must be a PARACategory enum"):
            CategorizationResult(
                category="project",  # String instead of enum
                confidence=0.8,
                reasoning="Test",
                suggested_tags=[]
            )

    def test_invalid_confidence_type(self):
        """Test validation of confidence type."""
        with pytest.raises(TypeError, match="Confidence must be a number"):
            CategorizationResult(
                category=PARACategory.PROJECT,
                confidence="high",  # String instead of number
                reasoning="Test",
                suggested_tags=[]
            )

    def test_confidence_out_of_range_high(self):
        """Test validation of confidence range - too high."""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            CategorizationResult(
                category=PARACategory.PROJECT,
                confidence=1.5,  # Above 1.0
                reasoning="Test",
                suggested_tags=[]
            )

    def test_confidence_out_of_range_low(self):
        """Test validation of confidence range - too low."""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            CategorizationResult(
                category=PARACategory.PROJECT,
                confidence=-0.1,  # Below 0.0
                reasoning="Test",
                suggested_tags=[]
            )

    def test_confidence_boundary_values(self):
        """Test confidence boundary values (0.0 and 1.0)."""
        # Test 0.0
        result_min = CategorizationResult(
            category=PARACategory.RESOURCE,
            confidence=0.0,
            reasoning="No confidence",
            suggested_tags=[]
        )
        assert result_min.confidence == 0.0
        
        # Test 1.0
        result_max = CategorizationResult(
            category=PARACategory.PROJECT,
            confidence=1.0,
            reasoning="Completely certain",
            suggested_tags=[]
        )
        assert result_max.confidence == 1.0

    def test_empty_reasoning(self):
        """Test validation of empty reasoning."""
        with pytest.raises(ValueError, match="Reasoning cannot be empty"):
            CategorizationResult(
                category=PARACategory.RESOURCE,
                confidence=0.5,
                reasoning="",  # Empty string
                suggested_tags=[]
            )

    def test_whitespace_only_reasoning(self):
        """Test validation of whitespace-only reasoning."""
        with pytest.raises(ValueError, match="Reasoning cannot be empty"):
            CategorizationResult(
                category=PARACategory.RESOURCE,
                confidence=0.5,
                reasoning="   ",  # Whitespace only
                suggested_tags=[]
            )

    def test_invalid_reasoning_type(self):
        """Test validation of reasoning type."""
        with pytest.raises(TypeError, match="Reasoning must be a string"):
            CategorizationResult(
                category=PARACategory.RESOURCE,
                confidence=0.5,
                reasoning=123,  # Number instead of string
                suggested_tags=[]
            )

    def test_invalid_suggested_tags_type(self):
        """Test validation of suggested_tags type."""
        with pytest.raises(TypeError, match="Suggested tags must be a list"):
            CategorizationResult(
                category=PARACategory.RESOURCE,
                confidence=0.5,
                reasoning="Test",
                suggested_tags="tag1,tag2"  # String instead of list
            )

    def test_invalid_tag_item_type(self):
        """Test validation of individual tag types."""
        with pytest.raises(TypeError, match="All suggested tags must be strings"):
            CategorizationResult(
                category=PARACategory.RESOURCE,
                confidence=0.5,
                reasoning="Test",
                suggested_tags=["valid_tag", 123]  # Number in list
            )

    def test_invalid_requires_review_type(self):
        """Test validation of requires_review type."""
        with pytest.raises(TypeError, match="Requires review must be a boolean"):
            CategorizationResult(
                category=PARACategory.RESOURCE,
                confidence=0.5,
                reasoning="Test",
                suggested_tags=[],
                requires_review="yes"  # String instead of boolean
            )

    def test_create_with_review(self):
        """Test create_with_review factory method."""
        result = CategorizationResult.create_with_review(
            category=PARACategory.AREA,
            confidence=0.6,
            reasoning="Uncertain categorization",
            suggested_tags=["review", "uncertain"]
        )
        
        assert result.category == PARACategory.AREA
        assert result.confidence == 0.6
        assert result.reasoning == "Uncertain categorization"
        assert result.suggested_tags == ["review", "uncertain"]
        assert result.requires_review is True

    def test_create_with_review_default_tags(self):
        """Test create_with_review with default tags."""
        result = CategorizationResult.create_with_review(
            category=PARACategory.PROJECT,
            confidence=0.4,
            reasoning="Low confidence project"
        )
        
        assert result.suggested_tags == []
        assert result.requires_review is True

    def test_create_confident(self):
        """Test create_confident factory method."""
        result = CategorizationResult.create_confident(
            category=PARACategory.PROJECT,
            reasoning="Clear project with explicit deadline",
            suggested_tags=["work", "deadline"]
        )
        
        assert result.category == PARACategory.PROJECT
        assert result.confidence == 1.0
        assert result.reasoning == "Clear project with explicit deadline"
        assert result.suggested_tags == ["work", "deadline"]
        assert result.requires_review is False

    def test_create_confident_default_tags(self):
        """Test create_confident with default tags."""
        result = CategorizationResult.create_confident(
            category=PARACategory.AREA,
            reasoning="Obvious area of responsibility"
        )
        
        assert result.suggested_tags == []
        assert result.requires_review is False

    def test_create_uncertain(self):
        """Test create_uncertain factory method."""
        result = CategorizationResult.create_uncertain(
            category=PARACategory.RESOURCE,
            reasoning="Unable to determine clear category",
            suggested_tags=["unclear", "needs_review"]
        )
        
        assert result.category == PARACategory.RESOURCE
        assert result.confidence == 0.3
        assert result.reasoning == "Unable to determine clear category"
        assert result.suggested_tags == ["unclear", "needs_review"]
        assert result.requires_review is True

    def test_is_confident_default_threshold(self):
        """Test is_confident with default threshold (0.7)."""
        high_confidence = CategorizationResult(
            category=PARACategory.PROJECT,
            confidence=0.8,
            reasoning="High confidence",
            suggested_tags=[]
        )
        
        low_confidence = CategorizationResult(
            category=PARACategory.RESOURCE,
            confidence=0.6,
            reasoning="Low confidence",
            suggested_tags=[]
        )
        
        assert high_confidence.is_confident() is True
        assert low_confidence.is_confident() is False

    def test_is_confident_custom_threshold(self):
        """Test is_confident with custom threshold."""
        result = CategorizationResult(
            category=PARACategory.AREA,
            confidence=0.75,
            reasoning="Medium confidence",
            suggested_tags=[]
        )
        
        assert result.is_confident(threshold=0.7) is True
        assert result.is_confident(threshold=0.8) is False

    def test_should_auto_categorize_high_confidence_no_review(self):
        """Test should_auto_categorize with high confidence and no review required."""
        result = CategorizationResult(
            category=PARACategory.PROJECT,
            confidence=0.9,
            reasoning="Very confident",
            suggested_tags=[],
            requires_review=False
        )
        
        assert result.should_auto_categorize() is True

    def test_should_auto_categorize_high_confidence_needs_review(self):
        """Test should_auto_categorize with high confidence but review required."""
        result = CategorizationResult(
            category=PARACategory.PROJECT,
            confidence=0.9,
            reasoning="Confident but needs validation",
            suggested_tags=[],
            requires_review=True
        )
        
        assert result.should_auto_categorize() is False

    def test_should_auto_categorize_low_confidence(self):
        """Test should_auto_categorize with low confidence."""
        result = CategorizationResult(
            category=PARACategory.RESOURCE,
            confidence=0.5,
            reasoning="Low confidence",
            suggested_tags=[],
            requires_review=False
        )
        
        assert result.should_auto_categorize() is False

    def test_should_auto_categorize_custom_threshold(self):
        """Test should_auto_categorize with custom confidence threshold."""
        result = CategorizationResult(
            category=PARACategory.AREA,
            confidence=0.75,
            reasoning="Medium confidence",
            suggested_tags=[],
            requires_review=False
        )
        
        assert result.should_auto_categorize(confidence_threshold=0.7) is True
        assert result.should_auto_categorize(confidence_threshold=0.8) is False

    def test_get_confidence_level_very_high(self):
        """Test confidence level description for very high confidence."""
        result = CategorizationResult(
            category=PARACategory.PROJECT,
            confidence=0.95,
            reasoning="Very high confidence",
            suggested_tags=[]
        )
        
        assert result.get_confidence_level() == "Very High"

    def test_get_confidence_level_high(self):
        """Test confidence level description for high confidence."""
        result = CategorizationResult(
            category=PARACategory.AREA,
            confidence=0.8,
            reasoning="High confidence",
            suggested_tags=[]
        )
        
        assert result.get_confidence_level() == "High"

    def test_get_confidence_level_medium(self):
        """Test confidence level description for medium confidence."""
        result = CategorizationResult(
            category=PARACategory.RESOURCE,
            confidence=0.6,
            reasoning="Medium confidence",
            suggested_tags=[]
        )
        
        assert result.get_confidence_level() == "Medium"

    def test_get_confidence_level_low(self):
        """Test confidence level description for low confidence."""
        result = CategorizationResult(
            category=PARACategory.RESOURCE,
            confidence=0.4,
            reasoning="Low confidence",
            suggested_tags=[]
        )
        
        assert result.get_confidence_level() == "Low"

    def test_get_confidence_level_very_low(self):
        """Test confidence level description for very low confidence."""
        result = CategorizationResult(
            category=PARACategory.RESOURCE,
            confidence=0.2,
            reasoning="Very low confidence",
            suggested_tags=[]
        )
        
        assert result.get_confidence_level() == "Very Low"

    def test_to_dict(self):
        """Test dictionary serialization."""
        result = CategorizationResult(
            category=PARACategory.PROJECT,
            confidence=0.85,
            reasoning="Clear project with deadline",
            suggested_tags=["work", "urgent"],
            requires_review=True
        )
        
        expected_dict = {
            "category": "project",
            "confidence": 0.85,
            "reasoning": "Clear project with deadline",
            "suggested_tags": ["work", "urgent"],
            "requires_review": True,
            "confidence_level": "High"
        }
        
        assert result.to_dict() == expected_dict

    def test_confidence_level_boundaries(self):
        """Test confidence level boundaries."""
        # Test boundary at 0.9
        result_90 = CategorizationResult(
            category=PARACategory.PROJECT,
            confidence=0.9,
            reasoning="Boundary test",
            suggested_tags=[]
        )
        assert result_90.get_confidence_level() == "Very High"
        
        result_89 = CategorizationResult(
            category=PARACategory.PROJECT,
            confidence=0.89,
            reasoning="Boundary test",
            suggested_tags=[]
        )
        assert result_89.get_confidence_level() == "High"
        
        # Test boundary at 0.7
        result_70 = CategorizationResult(
            category=PARACategory.PROJECT,
            confidence=0.7,
            reasoning="Boundary test",
            suggested_tags=[]
        )
        assert result_70.get_confidence_level() == "High"
        
        result_69 = CategorizationResult(
            category=PARACategory.PROJECT,
            confidence=0.69,
            reasoning="Boundary test",
            suggested_tags=[]
        )
        assert result_69.get_confidence_level() == "Medium"