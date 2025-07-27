"""Tests for ThoughtProcessingService."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from ...models.thought_content import ThoughtContent
from ...models.resource import Resource
from ...models.processing_status import ProcessingStatus
from ...models.para_category import PARACategory
from ...models.categorization_result import CategorizationResult
from ...services.thought_processing_service import (
    ThoughtProcessingService,
    ProcessingResult,
    ProcessingError,
    ValidationError,
    DuplicationError,
    CategorizationError,
    ResourceCreationError
)
from ...services.para_categorizer_service import PARACategorizerService


class TestProcessingResult:
    """Test ProcessingResult data class."""

    def test_success_result_creation(self):
        """Test creating a successful processing result."""
        thought = ThoughtContent.create_new(
            title="Test Thought", 
            content="Test content"
        )
        resource = Resource.create_new(
            title="Test Resource",
            content="Test content",
            category=PARACategory.RESOURCE
        )
        
        result = ProcessingResult.success_result(
            thought=thought,
            resource=resource,
            processing_time_ms=100
        )
        
        assert result.success is True
        assert result.thought == thought
        assert result.resource == resource
        assert result.error_message is None
        assert result.processing_time_ms == 100

    def test_failure_result_creation(self):
        """Test creating a failed processing result."""
        thought = ThoughtContent.create_new(
            title="Test Thought", 
            content="Test content"
        )
        
        result = ProcessingResult.failure_result(
            thought=thought,
            error_message="Processing failed",
            processing_time_ms=50
        )
        
        assert result.success is False
        assert result.thought == thought
        assert result.resource is None
        assert result.error_message == "Processing failed"
        assert result.processing_time_ms == 50


class TestProcessingExceptions:
    """Test custom processing exceptions."""

    def test_processing_error_inheritance(self):
        """Test that all processing errors inherit from ProcessingError."""
        assert issubclass(ValidationError, ProcessingError)
        assert issubclass(DuplicationError, ProcessingError)
        assert issubclass(CategorizationError, ProcessingError)
        assert issubclass(ResourceCreationError, ProcessingError)

    def test_exception_messages(self):
        """Test exception messages are preserved."""
        message = "Test error message"
        
        validation_error = ValidationError(message)
        assert str(validation_error) == message
        
        duplication_error = DuplicationError(message)
        assert str(duplication_error) == message
        
        categorization_error = CategorizationError(message)
        assert str(categorization_error) == message
        
        resource_error = ResourceCreationError(message)
        assert str(resource_error) == message


class TestThoughtProcessingServiceInitialization:
    """Test service initialization."""

    def test_initialization_requires_categorizer(self):
        """Test service requires categorizer service parameter."""
        mock_categorizer = Mock(spec=PARACategorizerService)
        service = ThoughtProcessingService(categorizer_service=mock_categorizer)
        assert service._categorizer == mock_categorizer

    def test_custom_categorizer_initialization(self):
        """Test service initializes with custom categorizer."""
        mock_categorizer = Mock(spec=PARACategorizerService)
        service = ThoughtProcessingService(categorizer_service=mock_categorizer)
        assert service._categorizer == mock_categorizer


class TestThoughtValidation:
    """Test thought validation logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_categorizer = Mock(spec=PARACategorizerService)
        self.service = ThoughtProcessingService(categorizer_service=self.mock_categorizer)

    def test_validate_valid_thought(self):
        """Test validation passes for valid thought."""
        thought = ThoughtContent.create_new(
            title="Valid Thought",
            content="Valid content"
        )
        
        # Should not raise any exception
        self.service._validate_thought(thought)

    def test_validate_none_thought(self):
        """Test validation fails for None thought."""
        with pytest.raises(ValidationError, match="Thought cannot be None"):
            self.service._validate_thought(None)

    def test_validate_empty_title(self):
        """Test validation fails for empty title."""
        # Since ThoughtContent.__post_init__ validates title, 
        # we test our service's handling of the domain model validation
        with pytest.raises(ValueError, match="Title cannot be empty"):
            ThoughtContent.create_new(
                title="   ",  # Empty/whitespace title
                content="Valid content"
            )

    def test_validate_empty_content(self):
        """Test validation fails for empty content."""
        # Create thought with valid content first, then manually create invalid one
        valid_thought = ThoughtContent.create_new(
            title="Valid Title",
            content="Valid content"
        )
        
        # Create invalid thought by manipulating the content
        from ...models.content_text import ContentText
        empty_content = ContentText.create("   ")  # Whitespace content
        
        invalid_thought = ThoughtContent(
            id=valid_thought.id,
            title="Valid Title",
            content=empty_content,
            created_date=valid_thought.created_date,
            processed=False,
            processing_status=ProcessingStatus.NEW
        )
        
        with pytest.raises(ValidationError, match="Thought content cannot be empty"):
            self.service._validate_thought(invalid_thought)

    def test_validate_invalid_processing_status(self):
        """Test validation fails for invalid processing status."""
        thought = ThoughtContent.create_new(
            title="Valid Thought",
            content="Valid content"
        )
        
        # Mark as processing then completed to get a completed thought
        processing_thought = thought.mark_as_processing()
        completed_thought = processing_thought.mark_as_completed()
        
        with pytest.raises(ValidationError, match="Thought cannot be processed in status"):
            self.service._validate_thought(completed_thought)


class TestProcessingWorkflow:
    """Test the main processing workflow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_categorizer = Mock(spec=PARACategorizerService)
        self.service = ThoughtProcessingService(categorizer_service=self.mock_categorizer)

    def test_successful_processing_workflow(self):
        """Test complete successful processing workflow."""
        # Setup
        thought = ThoughtContent.create_new(
            title="Test Thought",
            content="This is a test thought"
        )
        
        categorization_result = CategorizationResult.create_confident(
            category=PARACategory.RESOURCE,
            reasoning="Test categorization",
            suggested_tags=["test", "sample"]
        )
        
        self.mock_categorizer.categorize_thought.return_value = categorization_result
        
        # Execute  
        with patch.object(self.service, '_calculate_processing_time', return_value=100):
            result = self.service.process_thought(thought)
        
        # Verify
        assert result.success is True
        assert result.thought.processing_status == ProcessingStatus.COMPLETED
        assert result.thought.processed is True
        assert result.resource is not None
        assert result.resource.title == "Test Thought"
        assert result.resource.category == PARACategory.RESOURCE
        assert result.error_message is None
        assert result.processing_time_ms == 100
        
        # Verify categorizer was called with processing thought
        self.mock_categorizer.categorize_thought.assert_called_once()
        call_args = self.mock_categorizer.categorize_thought.call_args
        called_thought, called_context = call_args[0]
        assert called_thought.processing_status == ProcessingStatus.PROCESSING
        assert called_context is None

    def test_processing_with_user_context(self):
        """Test processing with user context."""
        thought = ThoughtContent.create_new(
            title="Test Thought",
            content="Test content"
        )
        
        user_context = {"user_id": "123", "preferences": {}}
        
        categorization_result = CategorizationResult.create_confident(
            category=PARACategory.PROJECT,
            reasoning="Test project",
            suggested_tags=["project"]
        )
        
        self.mock_categorizer.categorize_thought.return_value = categorization_result
        
        result = self.service.process_thought(thought, user_context)
        
        assert result.success is True
        # Verify categorizer was called with processing thought and user context
        self.mock_categorizer.categorize_thought.assert_called_once()
        call_args = self.mock_categorizer.categorize_thought.call_args
        called_thought, called_context = call_args[0]
        assert called_thought.processing_status == ProcessingStatus.PROCESSING
        assert called_context == user_context

    def test_processing_with_user_tags(self):
        """Test processing thought with user tags."""
        thought = ThoughtContent.create_new(
            title="Test Project",
            content="Project content",
            project_tag="MyProject",
            area_tag="Work"
        )
        
        categorization_result = CategorizationResult.create_confident(
            category=PARACategory.PROJECT,
            reasoning="User tagged as project",
            suggested_tags=["urgent"]
        )
        
        self.mock_categorizer.categorize_thought.return_value = categorization_result
        
        result = self.service.process_thought(thought)
        
        assert result.success is True
        assert result.resource is not None
        
        # Check that user tags were added to resource (with cleaned format)
        resource_tags = result.resource.tags.to_list()
        assert "project-myproject" in resource_tags
        assert "area-work" in resource_tags
        assert "urgent" in resource_tags

    def test_processing_failure_handling(self):
        """Test processing failure is handled gracefully."""
        thought = ThoughtContent.create_new(
            title="Test Thought",
            content="Test content"
        )
        
        # Make categorizer raise an exception
        self.mock_categorizer.categorize_thought.side_effect = Exception("Categorization failed")
        
        result = self.service.process_thought(thought)
        
        assert result.success is False
        assert result.thought.processing_status == ProcessingStatus.FAILED
        assert result.resource is None
        assert "Categorization failed" in result.error_message

    def test_validation_error_handling(self):
        """Test validation error is handled properly."""
        # Create thought with empty title
        thought = ThoughtContent.create_new(
            title="Valid",
            content="Valid content"
        )
        
        # Manually create invalid thought
        invalid_thought = ThoughtContent(
            id=thought.id,
            title="   ",  # Empty title
            content=thought.content,
            created_date=thought.created_date,
            processed=False,
            processing_status=ProcessingStatus.NEW
        )
        
        result = self.service.process_thought(invalid_thought)
        
        assert result.success is False
        assert "Thought title cannot be empty" in result.error_message
        assert result.thought.processing_status == ProcessingStatus.FAILED


class TestBatchProcessing:
    """Test batch processing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_categorizer = Mock(spec=PARACategorizerService)
        self.service = ThoughtProcessingService(categorizer_service=self.mock_categorizer)

    def test_empty_batch_processing(self):
        """Test processing empty list of thoughts."""
        results = self.service.process_thoughts_batch([])
        assert results == []

    def test_successful_batch_processing(self):
        """Test successful batch processing of multiple thoughts."""
        thoughts = [
            ThoughtContent.create_new(f"Thought {i}", f"Content {i}")
            for i in range(3)
        ]
        
        categorization_result = CategorizationResult.create_confident(
            category=PARACategory.RESOURCE,
            reasoning="Test",
            suggested_tags=[]
        )
        
        self.mock_categorizer.categorize_thought.return_value = categorization_result
        
        results = self.service.process_thoughts_batch(thoughts)
        
        assert len(results) == 3
        assert all(result.success for result in results)
        assert self.mock_categorizer.categorize_thought.call_count == 3

    def test_partial_batch_failure(self):
        """Test batch processing continues when some thoughts fail."""
        thoughts = [
            ThoughtContent.create_new(f"Thought {i}", f"Content {i}")
            for i in range(3)
        ]
        
        # Make second categorization fail
        categorization_result = CategorizationResult.create_confident(
            category=PARACategory.RESOURCE,
            reasoning="Test",
            suggested_tags=[]
        )
        
        self.mock_categorizer.categorize_thought.side_effect = [
            categorization_result,
            Exception("Categorization failed"),
            categorization_result
        ]
        
        results = self.service.process_thoughts_batch(thoughts)
        
        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is True


class TestRetryFunctionality:
    """Test retry processing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_categorizer = Mock(spec=PARACategorizerService)
        self.service = ThoughtProcessingService(categorizer_service=self.mock_categorizer)

    def test_retry_failed_thought(self):
        """Test retrying a failed thought."""
        thought = ThoughtContent.create_new(
            title="Test Thought",
            content="Test content"
        )
        
        # Mark as failed
        failed_thought = thought.mark_as_failed()
        
        # Setup successful retry
        categorization_result = CategorizationResult.create_confident(
            category=PARACategory.RESOURCE,
            reasoning="Retry successful",
            suggested_tags=[]
        )
        
        self.mock_categorizer.categorize_thought.return_value = categorization_result
        
        result = self.service.retry_failed_processing(failed_thought)
        
        assert result.success is True
        assert result.thought.processing_status == ProcessingStatus.COMPLETED

    def test_retry_non_failed_thought_raises_error(self):
        """Test retrying non-failed thought raises ValueError."""
        thought = ThoughtContent.create_new(
            title="Test Thought",
            content="Test content"
        )
        
        with pytest.raises(ValueError, match="Cannot retry processing for thought with status"):
            self.service.retry_failed_processing(thought)


class TestUtilityMethods:
    """Test utility and helper methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_categorizer = Mock(spec=PARACategorizerService)
        self.service = ThoughtProcessingService(categorizer_service=self.mock_categorizer)

    def test_can_process_thought_valid(self):
        """Test can_process_thought returns True for valid thought."""
        thought = ThoughtContent.create_new(
            title="Valid Thought",
            content="Valid content"
        )
        
        assert self.service.can_process_thought(thought) is True

    def test_can_process_thought_invalid(self):
        """Test can_process_thought returns False for invalid thought."""
        thought = ThoughtContent.create_new(
            title="Valid",
            content="Valid content"
        )
        
        # Mark as processing then completed to make it invalid for processing
        processing_thought = thought.mark_as_processing()
        completed_thought = processing_thought.mark_as_completed()
        
        assert self.service.can_process_thought(completed_thought) is False

    def test_processing_statistics_empty(self):
        """Test processing statistics for empty results."""
        stats = self.service.get_processing_statistics([])
        
        expected = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0.0,
            "average_processing_time_ms": 0.0
        }
        
        assert stats == expected

    def test_processing_statistics_with_results(self):
        """Test processing statistics calculation."""
        thought = ThoughtContent.create_new("Test", "Content")
        resource = Resource.create_new("Test", "Content", PARACategory.RESOURCE)
        
        results = [
            ProcessingResult.success_result(thought, resource, 100),
            ProcessingResult.success_result(thought, resource, 200),
            ProcessingResult.failure_result(thought, "Error", 50)
        ]
        
        stats = self.service.get_processing_statistics(results)
        
        assert stats["total_processed"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert stats["success_rate"] == 66.66666666666667
        assert stats["average_processing_time_ms"] == 116.66666666666667


class TestErrorHandling:
    """Test comprehensive error handling scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_categorizer = Mock(spec=PARACategorizerService)
        self.service = ThoughtProcessingService(categorizer_service=self.mock_categorizer)

    def test_categorization_error_handling(self):
        """Test handling of categorization errors."""
        thought = ThoughtContent.create_new(
            title="Test Thought",
            content="Test content"
        )
        
        self.mock_categorizer.categorize_thought.side_effect = Exception("Service unavailable")
        
        result = self.service.process_thought(thought)
        
        assert result.success is False
        assert "Categorization failed" in result.error_message
        assert "Service unavailable" in result.error_message

    def test_resource_creation_error_handling(self):
        """Test handling of resource creation errors."""
        thought = ThoughtContent.create_new(
            title="Test Thought",
            content="Test content"
        )
        
        # Create invalid categorization result that will cause resource creation to fail
        categorization_result = Mock()
        categorization_result.category = "InvalidCategory"  # Invalid enum value
        categorization_result.suggested_tags = []
        categorization_result.requires_review = False
        categorization_result.confidence = 0.8
        
        self.mock_categorizer.categorize_thought.return_value = categorization_result
        
        result = self.service.process_thought(thought)
        
        assert result.success is False
        assert "Resource creation failed" in result.error_message

    def test_mark_as_failed_edge_case(self):
        """Test marking as failed when thought is in invalid state."""
        thought = ThoughtContent.create_new(
            title="Test Thought",
            content="Test content"
        )
        
        # Mark as completed first
        completed_thought = thought.mark_as_completed()
        
        # Try to mark as failed - should handle gracefully
        result_thought = self.service._mark_as_failed(completed_thought, "Error")
        
        # Should return original thought since transition is invalid
        assert result_thought.processing_status == ProcessingStatus.COMPLETED


class TestProcessingWithCategorizationDetails:
    """Test processing with different categorization scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_categorizer = Mock(spec=PARACategorizerService)
        self.service = ThoughtProcessingService(categorizer_service=self.mock_categorizer)

    def test_processing_with_project_categorization(self):
        """Test processing thought categorized as project."""
        thought = ThoughtContent.create_new(
            title="Complete Report",
            content="Finish quarterly report by Friday"
        )
        
        categorization_result = CategorizationResult.create_confident(
            category=PARACategory.PROJECT,
            reasoning="Contains deadline and specific outcome",
            suggested_tags=["quarterly", "report", "deadline"]
        )
        
        self.mock_categorizer.categorize_thought.return_value = categorization_result
        
        result = self.service.process_thought(thought)
        
        assert result.success is True
        assert result.resource.category == PARACategory.PROJECT
        resource_tags = result.resource.tags.to_list()
        assert "quarterly" in resource_tags
        assert "report" in resource_tags
        assert "deadline" in resource_tags

    def test_processing_with_uncertain_categorization(self):
        """Test processing with uncertain categorization result."""
        thought = ThoughtContent.create_new(
            title="Random Thought",
            content="Some unclear content"
        )
        
        categorization_result = CategorizationResult.create_uncertain(
            category=PARACategory.RESOURCE,
            reasoning="Content is unclear, defaulting to resource",
            suggested_tags=[]
        )
        
        self.mock_categorizer.categorize_thought.return_value = categorization_result
        
        result = self.service.process_thought(thought)
        
        assert result.success is True
        assert result.resource.category == PARACategory.RESOURCE
        
        # Check that review tag was added
        resource_tags = result.resource.tags.to_list()
        assert "requires-review" in resource_tags
        assert any(tag.startswith("confidence-") for tag in resource_tags)

    def test_calculate_processing_time(self):
        """Test processing time calculation."""
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        
        with patch('datetime.datetime') as mock_datetime:
            end_time = datetime(2024, 1, 1, 12, 0, 0, 250000)  # 250ms later
            mock_datetime.utcnow.return_value = end_time
            
            processing_time = self.service._calculate_processing_time(start_time)
            
            assert processing_time == 250