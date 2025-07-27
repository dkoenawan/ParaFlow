"""ThoughtProcessingService for orchestrating complete thought-to-resource transformation.

This application service coordinates the complete workflow from thought intake
to resource creation, following hexagonal architecture principles.
"""

from dataclasses import dataclass
from datetime import datetime
import re

from ..models.thought_content import ThoughtContent
from ..models.resource import Resource
from ..models.processing_status import ProcessingStatus
from ..models.para_category import PARACategory
from .para_categorizer_service import PARACategorizerService


@dataclass(frozen=True)
class ProcessingResult:
    """Result of thought processing operation.
    
    Attributes:
        success: Whether processing completed successfully
        thought: The processed thought with updated status
        resource: Created resource (if successful)
        error_message: Error description (if failed)
        processing_time_ms: Time taken for processing
    """
    success: bool
    thought: ThoughtContent
    resource: Resource | None
    error_message: str | None
    processing_time_ms: int

    @classmethod
    def success_result(
        cls,
        thought: ThoughtContent,
        resource: Resource,
        processing_time_ms: int
    ) -> "ProcessingResult":
        """Create a successful processing result."""
        return cls(
            success=True,
            thought=thought,
            resource=resource,
            error_message=None,
            processing_time_ms=processing_time_ms
        )

    @classmethod
    def failure_result(
        cls,
        thought: ThoughtContent,
        error_message: str,
        processing_time_ms: int
    ) -> "ProcessingResult":
        """Create a failed processing result."""
        return cls(
            success=False,
            thought=thought,
            resource=None,
            error_message=error_message,
            processing_time_ms=processing_time_ms
        )


class ProcessingError(Exception):
    """Base exception for thought processing errors."""
    pass


class ValidationError(ProcessingError):
    """Exception raised when thought validation fails."""
    pass


class DuplicationError(ProcessingError):
    """Exception raised when duplicate thought is detected."""
    pass


class CategorizationError(ProcessingError):
    """Exception raised when categorization fails."""
    pass


class ResourceCreationError(ProcessingError):
    """Exception raised when resource creation fails."""
    pass


class ThoughtProcessingService:
    """Application service for orchestrating thought processing workflow.
    
    This service coordinates the complete thought-to-resource transformation:
    1. Validates thought content
    2. Checks for duplicates 
    3. Invokes categorization service
    4. Creates resource from classified content
    5. Updates processing status
    6. Handles errors and rollback
    
    Follows hexagonal architecture principles with clear separation of concerns.
    """

    def __init__(
        self,
        categorizer_service: PARACategorizerService
    ) -> None:
        """Initialize the thought processing service.
        
        Args:
            categorizer_service: Service for PARA categorization
        """
        self._categorizer = categorizer_service

    def process_thought(
        self,
        thought: ThoughtContent,
        user_context: dict[str, any] | None = None
    ) -> ProcessingResult:
        """Process a single thought through the complete workflow.
        
        This is the main orchestration method that coordinates all processing steps.
        
        Args:
            thought: The thought to process
            user_context: Optional context for personalized processing
            
        Returns:
            ProcessingResult with outcome and created resource
        """
        start_time = datetime.utcnow()
        processing_thought = None
        
        try:
            # Step 1: Validate thought content
            self._validate_thought(thought)
            
            # Step 2: Mark as processing and check for duplicates
            processing_thought = self._start_processing(thought)
            self._check_for_duplicates(processing_thought, user_context)
            
            # Step 3: Categorize the thought
            categorization_result = self._categorize_thought(
                processing_thought, user_context
            )
            
            # Step 4: Create resource from categorized content
            resource = self._create_resource(
                processing_thought, categorization_result, user_context
            )
            
            # Step 5: Mark processing as completed
            completed_thought = processing_thought.mark_as_completed()
            
            processing_time = self._calculate_processing_time(start_time)
            
            return ProcessingResult.success_result(
                thought=completed_thought,
                resource=resource,
                processing_time_ms=processing_time
            )
            
        except ProcessingError as e:
            # Handle known processing errors - use processing thought if available
            failed_thought = self._mark_as_failed(processing_thought or thought, str(e))
            processing_time = self._calculate_processing_time(start_time)
            
            return ProcessingResult.failure_result(
                thought=failed_thought,
                error_message=str(e),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            # Handle unexpected errors - use processing thought if available
            error_message = f"Unexpected error during processing: {str(e)}"
            failed_thought = self._mark_as_failed(processing_thought or thought, error_message)
            processing_time = self._calculate_processing_time(start_time)
            
            return ProcessingResult.failure_result(
                thought=failed_thought,
                error_message=error_message,
                processing_time_ms=processing_time
            )

    def process_thoughts_batch(
        self,
        thoughts: list[ThoughtContent],
        user_context: dict[str, any] | None = None
    ) -> list[ProcessingResult]:
        """Process multiple thoughts efficiently.
        
        Args:
            thoughts: List of thoughts to process
            user_context: Optional context for personalized processing
            
        Returns:
            List of ProcessingResult for each thought
        """
        if not thoughts:
            return []
        
        results = []
        
        for thought in thoughts:
            try:
                result = self.process_thought(thought, user_context)
                results.append(result)
                
            except Exception as e:
                # Ensure batch processing continues even if one thought fails
                error_message = f"Batch processing error: {str(e)}"
                failed_thought = self._mark_as_failed(thought, error_message)
                
                result = ProcessingResult.failure_result(
                    thought=failed_thought,
                    error_message=error_message,
                    processing_time_ms=0
                )
                results.append(result)
        
        return results

    def retry_failed_processing(
        self,
        thought: ThoughtContent,
        user_context: dict[str, any] | None = None
    ) -> ProcessingResult:
        """Retry processing for a previously failed thought.
        
        Args:
            thought: The failed thought to retry
            user_context: Optional context for processing
            
        Returns:
            ProcessingResult with retry outcome
            
        Raises:
            ValueError: If thought is not in FAILED status
        """
        if thought.processing_status != ProcessingStatus.FAILED:
            raise ValueError(
                f"Cannot retry processing for thought with status: "
                f"{thought.processing_status}. Only FAILED thoughts can be retried."
            )
        
        # Reset to NEW status for retry
        retry_thought = thought._update_status(
            ProcessingStatus.NEW, 
            processed=False
        )
        
        return self.process_thought(retry_thought, user_context)

    def _validate_thought(self, thought: ThoughtContent) -> None:
        """Validate thought content before processing.
        
        Args:
            thought: Thought to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not thought:
            raise ValidationError("Thought cannot be None")
        
        if not thought.title.strip():
            raise ValidationError("Thought title cannot be empty")
        
        if not thought.content.value.strip():
            raise ValidationError("Thought content cannot be empty")
        
        # Check if thought is in valid state for processing
        if thought.processing_status not in [ProcessingStatus.NEW, ProcessingStatus.FAILED]:
            raise ValidationError(
                f"Thought cannot be processed in status: {thought.processing_status}"
            )

    def _start_processing(self, thought: ThoughtContent) -> ThoughtContent:
        """Mark thought as processing and validate transition.
        
        Args:
            thought: Thought to start processing
            
        Returns:
            Thought with PROCESSING status
            
        Raises:
            ValidationError: If status transition is invalid
        """
        try:
            return thought.mark_as_processing()
        except ValueError as e:
            raise ValidationError(f"Cannot start processing: {str(e)}")

    def _check_for_duplicates(
        self,
        thought: ThoughtContent,
        user_context: dict[str, any] | None = None
    ) -> None:
        """Check for duplicate thoughts.
        
        Args:
            thought: Thought to check for duplicates
            user_context: Optional context for duplicate detection
            
        Raises:
            DuplicationError: If duplicate is detected
            
        Note:
            This is a placeholder implementation. Future versions should:
            - Check against existing thoughts in repository
            - Use content similarity algorithms
            - Consider user-specific duplicate rules
        """
        # TODO: Implement actual duplicate detection
        # For now, this is a placeholder that doesn't detect duplicates
        # Future implementation should:
        # 1. Query thought repository for similar content
        # 2. Use semantic similarity analysis
        # 3. Check user-defined duplicate rules
        # 4. Consider temporal aspects (recent duplicates vs old)
        pass

    def _categorize_thought(
        self,
        thought: ThoughtContent,
        user_context: dict[str, any] | None = None
    ) -> any:  # CategorizationResult type
        """Categorize thought using PARA methodology.
        
        Args:
            thought: Thought to categorize
            user_context: Optional context for categorization
            
        Returns:
            CategorizationResult from the categorizer service
            
        Raises:
            CategorizationError: If categorization fails
        """
        try:
            return self._categorizer.categorize_thought(thought, user_context)
        except Exception as e:
            raise CategorizationError(f"Categorization failed: {str(e)}")

    def _create_resource(
        self,
        thought: ThoughtContent,
        categorization_result: any,  # CategorizationResult type
        user_context: dict[str, any] | None = None
    ) -> Resource:
        """Create resource from processed thought and categorization.
        
        Args:
            thought: The processed thought
            categorization_result: Result from categorization service
            user_context: Optional context for resource creation
            
        Returns:
            Created Resource entity
            
        Raises:
            ResourceCreationError: If resource creation fails
        """
        try:
            # Extract suggested tags from categorization
            tags = categorization_result.suggested_tags.copy()
            
            # Add user tags if present (format compatible with ResourceTags validation)
            # TODO: Extract tag cleaning logic into a reusable guard clause/utility function
            # This logic should be shared across other services that need to clean user input
            # for ResourceTags compatibility (alphanumeric with hyphens/underscores only)
            if thought.project_tag:
                # Clean the tag to make it alphanumeric with hyphens/underscores
                clean_project = re.sub(r'[^a-z0-9_-]', '-', thought.project_tag.lower())
                tags.append(f"project-{clean_project}")
            if thought.area_tag:
                # Clean the tag to make it alphanumeric with hyphens/underscores  
                clean_area = re.sub(r'[^a-z0-9_-]', '-', thought.area_tag.lower())
                tags.append(f"area-{clean_area}")
            
            # Add confidence level as tag for review purposes (format: confidence-XX)
            if categorization_result.requires_review:
                tags.append("requires-review")
            
            confidence_level = int(categorization_result.confidence * 100)
            tags.append(f"confidence-{confidence_level:02d}")
            
            # Set deadline for projects if not specified
            deadline = None
            if categorization_result.category == PARACategory.PROJECT:
                # TODO: Extract deadline from content or use user context
                # For now, no automatic deadline setting
                pass
            
            # Create the resource
            resource = Resource.create_new(
                title=thought.title,
                content=thought.content.value,
                category=categorization_result.category,
                tags=tags,
                source_thought=thought.id,
                deadline=deadline
            )
            
            return resource
            
        except Exception as e:
            raise ResourceCreationError(f"Resource creation failed: {str(e)}")

    def _mark_as_failed(
        self,
        thought: ThoughtContent,
        error_message: str
    ) -> ThoughtContent:
        """Mark thought as failed with error handling.
        
        Args:
            thought: Thought to mark as failed
            error_message: Error message for logging
            
        Returns:
            Thought with FAILED status
        """
        try:
            return thought.mark_as_failed()
        except ValueError:
            # If we can't transition to FAILED, return original thought
            # This handles edge cases where thought is already in terminal state
            return thought

    def _calculate_processing_time(self, start_time: datetime) -> int:
        """Calculate processing time in milliseconds.
        
        Args:
            start_time: When processing started
            
        Returns:
            Processing time in milliseconds
        """
        end_time = datetime.utcnow()
        delta = end_time - start_time
        return int(delta.total_seconds() * 1000)

    # Status and health check methods

    def can_process_thought(self, thought: ThoughtContent) -> bool:
        """Check if a thought can be processed.
        
        Args:
            thought: Thought to check
            
        Returns:
            True if thought can be processed
        """
        try:
            self._validate_thought(thought)
            return True
        except ValidationError:
            return False

    def get_processing_statistics(
        self,
        results: list[ProcessingResult]
    ) -> dict[str, any]:
        """Get statistics from processing results.
        
        Args:
            results: List of processing results
            
        Returns:
            Dictionary with processing statistics
        """
        if not results:
            return {
                "total_processed": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0,
                "average_processing_time_ms": 0.0
            }
        
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        success_rate = (successful / total) * 100 if total > 0 else 0.0
        
        avg_time = (
            sum(r.processing_time_ms for r in results) / total 
            if total > 0 else 0.0
        )
        
        return {
            "total_processed": total,
            "successful": successful,
            "failed": failed,
            "success_rate": success_rate,
            "average_processing_time_ms": avg_time
        }