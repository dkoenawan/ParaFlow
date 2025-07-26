"""Tests for PARACategorizerService placeholder implementation."""

import pytest
from datetime import datetime

from packages.domain.services.para_categorizer_service import PARACategorizerService
from packages.domain.models.thought_content import ThoughtContent
from packages.domain.models.categorization_result import CategorizationResult
from packages.domain.models.para_category import PARACategory
from packages.domain.models.processing_status import ProcessingStatus


class TestPARACategorizerService:
    """Test cases for PARACategorizerService placeholder implementation."""

    @pytest.fixture
    def service(self):
        """Create a PARACategorizerService instance for testing."""
        return PARACategorizerService()

    @pytest.fixture
    def sample_thought(self):
        """Create a sample thought for testing."""
        return ThoughtContent.create_new(
            title="Sample Thought",
            content="This is a sample thought for testing categorization"
        )

    def test_service_initialization(self, service):
        """Test that service initializes properly."""
        assert isinstance(service, PARACategorizerService)

    def test_categorize_thought_basic(self, service, sample_thought):
        """Test basic thought categorization."""
        result = service.categorize_thought(sample_thought)
        
        assert isinstance(result, CategorizationResult)
        assert isinstance(result.category, PARACategory)
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.reasoning, str)
        assert len(result.reasoning) > 0
        assert isinstance(result.suggested_tags, list)

    def test_categorize_thought_with_project_tag(self, service):
        """Test categorization with explicit project tag."""
        thought = ThoughtContent.create_new(
            title="Quarterly Report",
            content="Need to finish the quarterly report",
            project_tag="quarterly-report"
        )
        
        result = service.categorize_thought(thought)
        
        assert result.category == PARACategory.PROJECT
        assert result.confidence == 1.0
        assert "quarterly-report" in result.suggested_tags
        assert "User explicitly tagged as project" in result.reasoning
        assert result.requires_review is False

    def test_categorize_thought_with_area_tag(self, service):
        """Test categorization with explicit area tag."""
        thought = ThoughtContent.create_new(
            title="Team Management",
            content="Remember to review team performance weekly",
            area_tag="team-management"
        )
        
        result = service.categorize_thought(thought)
        
        assert result.category == PARACategory.AREA
        assert result.confidence == 1.0
        assert "team-management" in result.suggested_tags
        assert "User explicitly tagged as area" in result.reasoning
        assert result.requires_review is False

    def test_categorize_thought_project_keywords(self, service):
        """Test categorization with project-related keywords."""
        thought = ThoughtContent.create_new(
            title="Website Redesign",
            content="Complete the website redesign by Friday deadline"
        )
        
        result = service.categorize_thought(thought)
        
        assert result.category == PARACategory.PROJECT
        assert result.confidence == 0.4  # Low confidence for keyword matching
        assert "project-related keywords" in result.reasoning
        assert result.requires_review is True

    def test_categorize_thought_area_keywords(self, service):
        """Test categorization with area-related keywords."""
        thought = ThoughtContent.create_new(
            title="Customer Relations",
            content="Daily routine for maintaining customer relationships"
        )
        
        result = service.categorize_thought(thought)
        
        assert result.category == PARACategory.AREA
        assert result.confidence == 0.4
        assert "area-related keywords" in result.reasoning
        assert result.requires_review is True

    def test_categorize_thought_default_resource(self, service):
        """Test default categorization to RESOURCE."""
        thought = ThoughtContent.create_new(
            title="Quantum Computing",
            content="Interesting article about quantum computing concepts"
        )
        
        result = service.categorize_thought(thought)
        
        assert result.category == PARACategory.RESOURCE
        assert result.confidence == 0.3  # Uncertain confidence
        assert "Defaulted to RESOURCE" in result.reasoning
        assert "Sophisticated LLM analysis needed" in result.reasoning
        assert result.requires_review is True

    def test_categorize_content_basic(self, service):
        """Test basic content categorization."""
        result = service.categorize_content(
            title="Sample Title",
            content="Sample content for testing",
            user_tags=None
        )
        
        assert isinstance(result, CategorizationResult)
        assert result.category == PARACategory.RESOURCE  # Default
        assert result.confidence == 0.3
        assert result.requires_review is True

    def test_categorize_content_with_user_tags(self, service):
        """Test content categorization with user tags."""
        result = service.categorize_content(
            title="Project Planning",
            content="Planning the new feature development",
            user_tags={"project_tag": "new-feature"}
        )
        
        assert result.category == PARACategory.PROJECT
        assert result.confidence == 1.0
        assert "new-feature" in result.suggested_tags

    def test_categorize_content_project_keywords_in_title(self, service):
        """Test project keyword detection in title."""
        result = service.categorize_content(
            title="Complete quarterly report by deadline",
            content="Regular content",
            user_tags=None
        )
        
        assert result.category == PARACategory.PROJECT
        assert result.confidence == 0.4
        assert "project-related keywords" in result.reasoning

    def test_categorize_content_multiple_keywords(self, service):
        """Test categorization with multiple matching keywords."""
        result = service.categorize_content(
            title="Project milestone",
            content="Need to complete task and deliver goal by deadline",
            user_tags=None
        )
        
        assert result.category == PARACategory.PROJECT
        assert result.confidence == 0.4

    def test_batch_categorize_empty_list(self, service):
        """Test batch categorization with empty list."""
        results = service.batch_categorize([])
        
        assert results == []

    def test_batch_categorize_single_thought(self, service, sample_thought):
        """Test batch categorization with single thought."""
        results = service.batch_categorize([sample_thought])
        
        assert len(results) == 1
        assert isinstance(results[0], CategorizationResult)

    def test_batch_categorize_multiple_thoughts(self, service):
        """Test batch categorization with multiple thoughts."""
        thoughts = [
            ThoughtContent.create_new(
                title="Test Project",
                content="Project with deadline",
                project_tag="test-project"
            ),
            ThoughtContent.create_new(
                title="Maintenance",
                content="Daily maintenance routine",
                area_tag="maintenance"
            ),
            ThoughtContent.create_new(
                title="Reference Material",
                content="Interesting reference material"
            )
        ]
        
        results = service.batch_categorize(thoughts)
        
        assert len(results) == 3
        assert results[0].category == PARACategory.PROJECT
        assert results[1].category == PARACategory.AREA
        assert results[2].category == PARACategory.RESOURCE

    def test_user_tag_priority_over_keywords(self, service):
        """Test that user tags take priority over keyword detection."""
        thought = ThoughtContent.create_new(
            title="Personal Development",
            content="This is a project with deadline and tasks to complete",
            area_tag="personal-development"
        )
        
        result = service.categorize_thought(thought)
        
        # Should be AREA due to user tag, not PROJECT despite keywords
        assert result.category == PARACategory.AREA
        assert result.confidence == 1.0
        assert "personal-development" in result.suggested_tags

    def test_case_insensitive_keyword_matching(self, service):
        """Test that keyword matching is case insensitive."""
        thought = ThoughtContent.create_new(
            title="URGENT PROJECT",
            content="COMPLETE THE PROJECT BY DEADLINE"
        )
        
        result = service.categorize_thought(thought)
        
        assert result.category == PARACategory.PROJECT

    def test_keyword_matching_in_combined_text(self, service):
        """Test keyword matching considers both title and content."""
        result = service.categorize_content(
            title="Important",
            content="deadline approaching",
            user_tags=None
        )
        
        assert result.category == PARACategory.PROJECT

    def test_placeholder_categorization_no_user_tags(self, service):
        """Test placeholder categorization when no user tags provided."""
        result = service._placeholder_categorization(
            title="Sample",
            content="Some neutral content",
            user_tags=None
        )
        
        assert result.category == PARACategory.RESOURCE
        assert result.confidence == 0.3

    def test_placeholder_categorization_empty_user_tags(self, service):
        """Test placeholder categorization with empty user tags dict."""
        result = service._placeholder_categorization(
            title="Sample",
            content="Some neutral content",
            user_tags={}
        )
        
        assert result.category == PARACategory.RESOURCE
        assert result.confidence == 0.3

    def test_user_context_parameter_accepted(self, service, sample_thought):
        """Test that user_context parameter is accepted (for future use)."""
        user_context = {"existing_projects": ["project1"], "areas": ["area1"]}
        
        # Should not raise an error
        result = service.categorize_thought(sample_thought, user_context)
        assert isinstance(result, CategorizationResult)

    def test_all_project_keywords(self, service):
        """Test all project-related keywords are detected."""
        project_keywords = [
            "deadline", "due", "complete by", "finish", "deliver",
            "project", "goal", "milestone", "task", "todo"
        ]
        
        for keyword in project_keywords:
            thought = ThoughtContent.create_new(
                title=f"Test {keyword}",
                content=f"This is about {keyword}"
            )
            
            result = service.categorize_thought(thought)
            assert result.category == PARACategory.PROJECT, f"Keyword '{keyword}' not detected"

    def test_all_area_keywords(self, service):
        """Test all area-related keywords are detected."""
        area_keywords = [
            "maintain", "ongoing", "responsibility", "regular",
            "daily", "weekly", "routine", "habit"
        ]
        
        for keyword in area_keywords:
            thought = ThoughtContent.create_new(
                title=f"Test {keyword}",
                content=f"This is about {keyword} activities"
            )
            
            result = service.categorize_thought(thought)
            assert result.category == PARACategory.AREA, f"Keyword '{keyword}' not detected"

    def test_future_methods_not_implemented(self, service, sample_thought):
        """Test that future methods raise NotImplementedError."""
        result = CategorizationResult.create_uncertain(
            PARACategory.RESOURCE, "test"
        )
        
        with pytest.raises(NotImplementedError):
            service.learn_from_feedback(sample_thought, PARACategory.PROJECT, result)
        
        with pytest.raises(NotImplementedError):
            service.get_category_suggestions("content", {})
        
        with pytest.raises(NotImplementedError):
            service.explain_categorization(result)

    def test_empty_content_handling(self, service):
        """Test handling of empty content."""
        thought = ThoughtContent.create_new(
            title="Empty Content",
            content="placeholder"  # ThoughtContent requires non-empty content
        )
        
        result = service.categorize_thought(thought)
        
        # Should default to RESOURCE
        assert result.category == PARACategory.RESOURCE
        assert result.requires_review is True

    def test_whitespace_only_content(self, service):
        """Test handling of whitespace-only content."""
        thought = ThoughtContent.create_new(
            title="Whitespace Content",
            content="   \n\t  "
        )
        
        result = service.categorize_thought(thought)
        
        assert result.category == PARACategory.RESOURCE
        assert result.requires_review is True

    def test_very_long_content(self, service):
        """Test handling of very long content."""
        long_content = "word " * 1000 + "deadline project"
        thought = ThoughtContent.create_new(
            title="Long Content",
            content=long_content
        )
        
        result = service.categorize_thought(thought)
        
        # Should still detect keywords
        assert result.category == PARACategory.PROJECT

    def test_mixed_case_user_tags(self, service):
        """Test user tags with mixed case values."""
        thought = ThoughtContent.create_new(
            title="My Project",
            content="Sample content",
            project_tag="My-Project-Name"
        )
        
        result = service.categorize_thought(thought)
        
        assert result.category == PARACategory.PROJECT
        assert "My-Project-Name" in result.suggested_tags

    def test_both_project_and_area_tags(self, service):
        """Test behavior when both project and area tags are present."""
        thought = ThoughtContent.create_new(
            title="Mixed Tags",
            content="Sample content",
            project_tag="test-project",
            area_tag="test-area"
        )
        
        result = service.categorize_thought(thought)
        
        # Should prioritize project_tag (checked first)
        assert result.category == PARACategory.PROJECT
        assert "test-project" in result.suggested_tags

    def test_confidence_levels_for_different_scenarios(self, service):
        """Test that different scenarios produce appropriate confidence levels."""
        # High confidence: explicit user tag
        thought_high = ThoughtContent.create_new(
            title="Test Project",
            content="Sample",
            project_tag="test"
        )
        result_high = service.categorize_thought(thought_high)
        assert result_high.confidence == 1.0
        
        # Medium confidence: keyword match
        thought_medium = ThoughtContent.create_new(
            title="Task Management",
            content="Complete this task by deadline"
        )
        result_medium = service.categorize_thought(thought_medium)
        assert result_medium.confidence == 0.4
        
        # Low confidence: default fallback
        thought_low = ThoughtContent.create_new(
            title="Random Thoughts",
            content="Random thoughts"
        )
        result_low = service.categorize_thought(thought_low)
        assert result_low.confidence == 0.3