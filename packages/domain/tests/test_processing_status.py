"""Tests for ProcessingStatus enum."""

import pytest
from packages.domain.models.processing_status import ProcessingStatus


class TestProcessingStatus:
    """Test cases for ProcessingStatus enum."""

    def test_enum_values(self) -> None:
        """Test that all expected enum values exist."""
        assert ProcessingStatus.PENDING.value == "pending"
        assert ProcessingStatus.PROCESSING.value == "processing"
        assert ProcessingStatus.COMPLETED.value == "completed"
        assert ProcessingStatus.FAILED.value == "failed"
        assert ProcessingStatus.SKIPPED.value == "skipped"

    def test_string_representation(self) -> None:
        """Test string representation of enum values."""
        assert str(ProcessingStatus.PENDING) == "pending"
        assert str(ProcessingStatus.PROCESSING) == "processing"
        assert str(ProcessingStatus.COMPLETED) == "completed"
        assert str(ProcessingStatus.FAILED) == "failed"
        assert str(ProcessingStatus.SKIPPED) == "skipped"

    def test_from_string_valid_values(self) -> None:
        """Test creating enum from valid string values."""
        assert ProcessingStatus.from_string("pending") == ProcessingStatus.PENDING
        assert ProcessingStatus.from_string("processing") == ProcessingStatus.PROCESSING
        assert ProcessingStatus.from_string("completed") == ProcessingStatus.COMPLETED
        assert ProcessingStatus.from_string("failed") == ProcessingStatus.FAILED
        assert ProcessingStatus.from_string("skipped") == ProcessingStatus.SKIPPED

    def test_from_string_case_insensitive(self) -> None:
        """Test that from_string is case insensitive."""
        assert ProcessingStatus.from_string("PENDING") == ProcessingStatus.PENDING
        assert ProcessingStatus.from_string("Processing") == ProcessingStatus.PROCESSING
        assert ProcessingStatus.from_string("COMPLETED") == ProcessingStatus.COMPLETED

    def test_from_string_invalid_value(self) -> None:
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid processing status: invalid"):
            ProcessingStatus.from_string("invalid")

    def test_valid_transitions_from_pending(self) -> None:
        """Test valid transitions from PENDING status."""
        pending = ProcessingStatus.PENDING
        
        assert pending.can_transition_to(ProcessingStatus.PROCESSING) is True
        assert pending.can_transition_to(ProcessingStatus.SKIPPED) is True
        assert pending.can_transition_to(ProcessingStatus.COMPLETED) is False
        assert pending.can_transition_to(ProcessingStatus.FAILED) is False
        assert pending.can_transition_to(ProcessingStatus.PENDING) is False

    def test_valid_transitions_from_processing(self) -> None:
        """Test valid transitions from PROCESSING status."""
        processing = ProcessingStatus.PROCESSING
        
        assert processing.can_transition_to(ProcessingStatus.COMPLETED) is True
        assert processing.can_transition_to(ProcessingStatus.FAILED) is True
        assert processing.can_transition_to(ProcessingStatus.PENDING) is False
        assert processing.can_transition_to(ProcessingStatus.PROCESSING) is False
        assert processing.can_transition_to(ProcessingStatus.SKIPPED) is False

    def test_valid_transitions_from_failed(self) -> None:
        """Test valid transitions from FAILED status (allow retry)."""
        failed = ProcessingStatus.FAILED
        
        assert failed.can_transition_to(ProcessingStatus.PROCESSING) is True
        assert failed.can_transition_to(ProcessingStatus.PENDING) is False
        assert failed.can_transition_to(ProcessingStatus.COMPLETED) is False
        assert failed.can_transition_to(ProcessingStatus.FAILED) is False
        assert failed.can_transition_to(ProcessingStatus.SKIPPED) is False

    def test_no_transitions_from_completed(self) -> None:
        """Test that COMPLETED is a final state with no valid transitions."""
        completed = ProcessingStatus.COMPLETED
        
        assert completed.can_transition_to(ProcessingStatus.PENDING) is False
        assert completed.can_transition_to(ProcessingStatus.PROCESSING) is False
        assert completed.can_transition_to(ProcessingStatus.COMPLETED) is False
        assert completed.can_transition_to(ProcessingStatus.FAILED) is False
        assert completed.can_transition_to(ProcessingStatus.SKIPPED) is False

    def test_no_transitions_from_skipped(self) -> None:
        """Test that SKIPPED is a final state with no valid transitions."""
        skipped = ProcessingStatus.SKIPPED
        
        assert skipped.can_transition_to(ProcessingStatus.PENDING) is False
        assert skipped.can_transition_to(ProcessingStatus.PROCESSING) is False
        assert skipped.can_transition_to(ProcessingStatus.COMPLETED) is False
        assert skipped.can_transition_to(ProcessingStatus.FAILED) is False
        assert skipped.can_transition_to(ProcessingStatus.SKIPPED) is False