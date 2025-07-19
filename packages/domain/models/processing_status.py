"""Processing status enumeration for thought processing lifecycle."""

from enum import Enum


class ProcessingStatus(Enum):
    """Enumeration of possible processing states for thought content.
    
    States represent the lifecycle of a thought from intake to completion:
    - PENDING: New thought awaiting processing
    - PROCESSING: Currently being analyzed by Claude
    - COMPLETED: Successfully processed and categorized
    - FAILED: Processing failed, requires attention
    - SKIPPED: Duplicate or invalid content
    """
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

    def __str__(self) -> str:
        """Return the string representation of the status."""
        return self.value

    @classmethod
    def from_string(cls, status: str) -> "ProcessingStatus":
        """Create ProcessingStatus from string value.
        
        Args:
            status: String representation of the status
            
        Returns:
            ProcessingStatus enum value
            
        Raises:
            ValueError: If status string is not valid
        """
        try:
            return cls(status.lower())
        except ValueError:
            valid_statuses = [s.value for s in cls]
            raise ValueError(
                f"Invalid processing status: {status}. "
                f"Valid statuses are: {', '.join(valid_statuses)}"
            )

    def can_transition_to(self, new_status: "ProcessingStatus") -> bool:
        """Check if this status can transition to another status.
        
        Valid transitions:
        - PENDING -> PROCESSING, SKIPPED
        - PROCESSING -> COMPLETED, FAILED
        - FAILED -> PROCESSING (retry)
        - COMPLETED/SKIPPED are final states
        
        Args:
            new_status: The status to transition to
            
        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions = {
            ProcessingStatus.PENDING: {ProcessingStatus.PROCESSING, ProcessingStatus.SKIPPED},
            ProcessingStatus.PROCESSING: {ProcessingStatus.COMPLETED, ProcessingStatus.FAILED},
            ProcessingStatus.FAILED: {ProcessingStatus.PROCESSING},  # Allow retry
            ProcessingStatus.COMPLETED: set(),  # Final state
            ProcessingStatus.SKIPPED: set(),  # Final state
        }
        
        return new_status in valid_transitions.get(self, set())