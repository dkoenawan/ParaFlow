"""Tests for ThoughtContent domain entity."""

import uuid
from datetime import datetime, timedelta
import pytest
from packages.domain.models.thought_content import ThoughtContent
from packages.domain.models.thought_id import ThoughtId
from packages.domain.models.content_text import ContentText
from packages.domain.models.processing_status import ProcessingStatus


class TestThoughtContent:
    """Test cases for ThoughtContent domain entity."""

    def test_create_new_with_minimal_parameters(self) -> None:
        """Test creating new thought with minimal required parameters."""
        thought = ThoughtContent.create_new(
            title="Test Thought",
            content="This is a test thought"
        )
        
        assert thought.title == "Test Thought"
        assert thought.content.value == "This is a test thought"
        assert thought.processed is False
        assert thought.processing_status == ProcessingStatus.NEW
        assert thought.project_tag is None
        assert thought.area_tag is None
        assert isinstance(thought.id, ThoughtId)
        assert isinstance(thought.created_date, datetime)

    def test_create_new_with_all_parameters(self) -> None:
        """Test creating new thought with all parameters."""
        created_date = datetime.utcnow()
        
        thought = ThoughtContent.create_new(
            title="Complete Thought",
            content="Full thought content",
            project_tag="My Project",
            area_tag="My Area",
            created_date=created_date
        )
        
        assert thought.title == "Complete Thought"
        assert thought.content.value == "Full thought content"
        assert thought.project_tag == "My Project"
        assert thought.area_tag == "My Area"
        assert thought.created_date == created_date

    def test_create_new_with_empty_title_raises_error(self) -> None:
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            ThoughtContent.create_new(
                title="   ",  # Whitespace only
                content="Content"
            )

    def test_restore_from_storage(self) -> None:
        """Test restoring thought from storage data."""
        id_string = str(uuid.uuid4())
        created_date = datetime.utcnow()
        
        thought = ThoughtContent.restore(
            id_value=id_string,
            title="Restored Thought",
            content="Restored content",
            created_date=created_date,
            processed=True,
            processing_status="completed",
            project_tag="Project A",
            area_tag="Area B"
        )
        
        assert str(thought.id) == id_string
        assert thought.title == "Restored Thought"
        assert thought.content.value == "Restored content"
        assert thought.created_date == created_date
        assert thought.processed is True
        assert thought.processing_status == ProcessingStatus.COMPLETED
        assert thought.project_tag == "Project A"
        assert thought.area_tag == "Area B"

    def test_mark_as_processing_from_pending(self) -> None:
        """Test marking thought as processing from pending status."""
        thought = ThoughtContent.create_new("Test", "Content")
        
        processing_thought = thought.mark_as_processing()
        
        assert processing_thought.processing_status == ProcessingStatus.PROCESSING
        assert processing_thought.processed is False
        assert thought.processing_status == ProcessingStatus.NEW  # Original unchanged

    def test_mark_as_processing_invalid_transition(self) -> None:
        """Test that invalid transition to processing raises error."""
        thought = ThoughtContent.create_new("Test", "Content")
        completed_thought = thought.mark_as_processing().mark_as_completed()
        
        with pytest.raises(ValueError, match="Cannot transition from completed to PROCESSING"):
            completed_thought.mark_as_processing()

    def test_mark_as_completed_from_processing(self) -> None:
        """Test marking thought as completed from processing status."""
        thought = ThoughtContent.create_new("Test", "Content")
        processing_thought = thought.mark_as_processing()
        
        completed_thought = processing_thought.mark_as_completed()
        
        assert completed_thought.processing_status == ProcessingStatus.COMPLETED
        assert completed_thought.processed is True

    def test_mark_as_completed_invalid_transition(self) -> None:
        """Test that invalid transition to completed raises error."""
        thought = ThoughtContent.create_new("Test", "Content")
        
        with pytest.raises(ValueError, match="Cannot transition from pending to COMPLETED"):
            thought.mark_as_completed()

    def test_mark_as_failed_from_processing(self) -> None:
        """Test marking thought as failed from processing status."""
        thought = ThoughtContent.create_new("Test", "Content")
        processing_thought = thought.mark_as_processing()
        
        failed_thought = processing_thought.mark_as_failed()
        
        assert failed_thought.processing_status == ProcessingStatus.FAILED
        assert failed_thought.processed is False

    def test_mark_as_skipped_from_pending(self) -> None:
        """Test marking thought as skipped from pending status."""
        thought = ThoughtContent.create_new("Test", "Content")
        
        skipped_thought = thought.mark_as_skipped()
        
        assert skipped_thought.processing_status == ProcessingStatus.SKIPPED
        assert skipped_thought.processed is True

    def test_retry_after_failure(self) -> None:
        """Test that failed thoughts can be retried."""
        thought = ThoughtContent.create_new("Test", "Content")
        failed_thought = thought.mark_as_processing().mark_as_failed()
        
        retry_thought = failed_thought.mark_as_processing()
        
        assert retry_thought.processing_status == ProcessingStatus.PROCESSING

    def test_has_user_tags_with_both_tags(self) -> None:
        """Test has_user_tags when both tags are set."""
        thought = ThoughtContent.create_new(
            "Test", 
            "Content",
            project_tag="Project",
            area_tag="Area"
        )
        
        assert thought.has_user_tags() is True

    def test_has_user_tags_with_project_only(self) -> None:
        """Test has_user_tags when only project tag is set."""
        thought = ThoughtContent.create_new(
            "Test", 
            "Content",
            project_tag="Project"
        )
        
        assert thought.has_user_tags() is True

    def test_has_user_tags_with_area_only(self) -> None:
        """Test has_user_tags when only area tag is set."""
        thought = ThoughtContent.create_new(
            "Test", 
            "Content",
            area_tag="Area"
        )
        
        assert thought.has_user_tags() is True

    def test_has_user_tags_with_no_tags(self) -> None:
        """Test has_user_tags when no tags are set."""
        thought = ThoughtContent.create_new("Test", "Content")
        
        assert thought.has_user_tags() is False

    def test_get_content_preview_short_content(self) -> None:
        """Test content preview with short content."""
        thought = ThoughtContent.create_new("Test", "Short content")
        
        preview = thought.get_content_preview(50)
        
        assert preview == "Short content"

    def test_get_content_preview_long_content(self) -> None:
        """Test content preview with long content."""
        long_content = "This is a very long content that should be truncated"
        thought = ThoughtContent.create_new("Test", long_content)
        
        preview = thought.get_content_preview(20)
        
        assert len(preview) == 20
        assert preview.endswith("...")

    def test_string_representation(self) -> None:
        """Test string representation of ThoughtContent."""
        thought = ThoughtContent.create_new("My Thought", "Content")
        
        str_repr = str(thought)
        
        assert "ThoughtContent" in str_repr
        assert "My Thought" in str_repr
        assert str(thought.id) in str_repr

    def test_repr_representation(self) -> None:
        """Test detailed repr representation."""
        thought = ThoughtContent.create_new("Test", "Content")
        
        repr_str = repr(thought)
        
        assert "ThoughtContent(" in repr_str
        assert "title='Test'" in repr_str
        assert "status=pending" in repr_str
        assert "processed=False" in repr_str

    def test_immutability(self) -> None:
        """Test that ThoughtContent is immutable."""
        thought = ThoughtContent.create_new("Test", "Content")
        
        with pytest.raises(Exception):  # dataclass.FrozenInstanceError
            thought.title = "Changed"  # type: ignore

    def test_validation_title_type(self) -> None:
        """Test validation of title type."""
        with pytest.raises(TypeError, match="Title must be a string"):
            ThoughtContent(
                id=ThoughtId.generate(),
                title=123,  # type: ignore
                content=ContentText("Content"),
                created_date=datetime.utcnow(),
                processed=False,
                processing_status=ProcessingStatus.NEW
            )

    def test_validation_content_type(self) -> None:
        """Test validation of content type."""
        with pytest.raises(TypeError, match="Content must be a ContentText object"):
            ThoughtContent(
                id=ThoughtId.generate(),
                title="Title",
                content="Not ContentText",  # type: ignore
                created_date=datetime.utcnow(),
                processed=False,
                processing_status=ProcessingStatus.NEW
            )

    def test_validation_processed_type(self) -> None:
        """Test validation of processed flag type."""
        with pytest.raises(TypeError, match="Processed must be a boolean"):
            ThoughtContent(
                id=ThoughtId.generate(),
                title="Title",
                content=ContentText("Content"),
                created_date=datetime.utcnow(),
                processed="yes",  # type: ignore
                processing_status=ProcessingStatus.NEW
            )

    def test_validation_processing_status_type(self) -> None:
        """Test validation of processing status type."""
        with pytest.raises(TypeError, match="Processing status must be a ProcessingStatus enum"):
            ThoughtContent(
                id=ThoughtId.generate(),
                title="Title",
                content=ContentText("Content"),
                created_date=datetime.utcnow(),
                processed=False,
                processing_status="pending"  # type: ignore
            )

    def test_validation_project_tag_type(self) -> None:
        """Test validation of project tag type."""
        with pytest.raises(TypeError, match="Project tag must be a string or None"):
            ThoughtContent(
                id=ThoughtId.generate(),
                title="Title",
                content=ContentText("Content"),
                created_date=datetime.utcnow(),
                processed=False,
                processing_status=ProcessingStatus.NEW,
                project_tag=123  # type: ignore
            )

    def test_validation_area_tag_type(self) -> None:
        """Test validation of area tag type."""
        with pytest.raises(TypeError, match="Area tag must be a string or None"):
            ThoughtContent(
                id=ThoughtId.generate(),
                title="Title",
                content=ContentText("Content"),
                created_date=datetime.utcnow(),
                processed=False,
                processing_status=ProcessingStatus.NEW,
                area_tag=123  # type: ignore
            )

    def test_free_form_content_no_limits(self) -> None:
        """Test that content has no length restrictions."""
        very_long_content = "A" * 10000  # 10k characters
        
        thought = ThoughtContent.create_new(
            "Long Thought",
            very_long_content
        )
        
        assert thought.content.value == very_long_content
        assert len(thought.content.value) == 10000

    def test_supports_unicode_content(self) -> None:
        """Test that thought supports Unicode content."""
        unicode_content = "Thinking about 🌍 世界 and 🚀 space exploration"
        
        thought = ThoughtContent.create_new(
            "Unicode Thought",
            unicode_content
        )
        
        assert thought.content.value == unicode_content

    def test_supports_multiline_content(self) -> None:
        """Test that thought supports multiline content."""
        multiline_content = """Line 1: First thought
Line 2: Second thought
Line 3: Third thought"""
        
        thought = ThoughtContent.create_new(
            "Multiline Thought",
            multiline_content
        )
        
        assert thought.content.value == multiline_content