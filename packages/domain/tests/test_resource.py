"""Tests for Resource domain entity."""

import pytest
from datetime import datetime, timedelta
from packages.domain.models.resource import Resource
from packages.domain.models.resource_id import ResourceId
from packages.domain.models.content_text import ContentText
from packages.domain.models.para_category import PARACategory
from packages.domain.models.resource_tags import ResourceTags
from packages.domain.models.thought_id import ThoughtId


class TestResource:
    """Test cases for Resource domain entity."""

    def test_create_new_resource(self):
        """Test creating a new resource with minimal parameters."""
        resource = Resource.create_new(
            title="Test Resource",
            content="This is test content",
            category=PARACategory.PROJECT
        )
        
        assert isinstance(resource, Resource)
        assert isinstance(resource.id, ResourceId)
        assert resource.title == "Test Resource"
        assert str(resource.content) == "This is test content"
        assert resource.category == PARACategory.PROJECT
        assert resource.tags.is_empty()
        assert resource.source_thought is None
        assert resource.deadline is None
        assert isinstance(resource.created_date, datetime)
        assert resource.updated_date == resource.created_date

    def test_create_new_with_all_parameters(self):
        """Test creating a new resource with all parameters."""
        source_thought = ThoughtId.generate()
        deadline = datetime.utcnow() + timedelta(days=7)
        created_date = datetime.utcnow() - timedelta(hours=1)
        
        resource = Resource.create_new(
            title="Complete Project",
            content="Detailed project description",
            category=PARACategory.PROJECT,
            tags=["work", "urgent"],
            source_thought=source_thought,
            deadline=deadline,
            created_date=created_date
        )
        
        assert resource.title == "Complete Project"
        assert resource.category == PARACategory.PROJECT
        assert len(resource.tags) == 2
        assert "work" in resource.tags
        assert "urgent" in resource.tags
        assert resource.source_thought == source_thought
        assert resource.deadline == deadline
        assert resource.created_date == created_date

    def test_create_new_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Resource.create_new(
                title="",
                content="Content",
                category=PARACategory.PROJECT
            )
        
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Resource.create_new(
                title="   ",
                content="Content",
                category=PARACategory.PROJECT
            )

    def test_restore_from_storage(self):
        """Test restoring resource from persistent storage."""
        resource_id = ResourceId.generate()
        thought_id = ThoughtId.generate()
        created_date = datetime.utcnow() - timedelta(hours=2)
        updated_date = datetime.utcnow() - timedelta(hours=1)
        deadline = datetime.utcnow() + timedelta(days=5)
        
        resource = Resource.restore(
            id_value=str(resource_id),
            title="Restored Resource",
            content="Restored content",
            category="project",
            tags=["work", "restored"],
            source_thought_id=str(thought_id),
            created_date=created_date,
            updated_date=updated_date,
            deadline=deadline
        )
        
        assert resource.id == resource_id
        assert resource.title == "Restored Resource"
        assert resource.category == PARACategory.PROJECT
        assert len(resource.tags) == 2
        assert resource.source_thought == thought_id
        assert resource.created_date == created_date
        assert resource.updated_date == updated_date
        assert resource.deadline == deadline

    def test_restore_without_source_thought(self):
        """Test restoring resource without source thought."""
        resource = Resource.restore(
            id_value=str(ResourceId.generate()),
            title="No Source Resource",
            content="Content",
            category="area",
            tags=[],
            source_thought_id=None,
            created_date=datetime.utcnow(),
            updated_date=datetime.utcnow()
        )
        
        assert resource.source_thought is None

    def test_update_content(self):
        """Test updating resource content."""
        resource = Resource.create_new(
            title="Test",
            content="Original content",
            category=PARACategory.RESOURCE
        )
        
        updated = resource.update_content("New content")
        
        assert resource.content != updated.content  # Original unchanged
        assert str(updated.content) == "New content"
        assert updated.updated_date > resource.updated_date
        assert updated.id == resource.id  # Same ID

    def test_update_category_valid_transition(self):
        """Test updating category with valid transition."""
        resource = Resource.create_new(
            title="Test",
            content="Content",
            category=PARACategory.PROJECT
        )
        
        updated = resource.update_category(PARACategory.ARCHIVE)
        
        assert resource.category == PARACategory.PROJECT  # Original unchanged
        assert updated.category == PARACategory.ARCHIVE
        assert updated.updated_date > resource.updated_date

    def test_update_category_invalid_transition(self):
        """Test updating category with invalid transition raises error."""
        resource = Resource.create_new(
            title="Test",
            content="Content",
            category=PARACategory.PROJECT
        )
        
        with pytest.raises(ValueError, match="Cannot transition from"):
            resource.update_category(PARACategory.RESOURCE)

    def test_add_tag(self):
        """Test adding a tag to resource."""
        resource = Resource.create_new(
            title="Test",
            content="Content",
            category=PARACategory.RESOURCE,
            tags=["existing"]
        )
        
        updated = resource.add_tag("new-tag")
        
        assert len(resource.tags) == 1  # Original unchanged
        assert len(updated.tags) == 2
        assert "existing" in updated.tags
        assert "new-tag" in updated.tags

    def test_remove_tag(self):
        """Test removing a tag from resource."""
        resource = Resource.create_new(
            title="Test",
            content="Content",
            category=PARACategory.RESOURCE,
            tags=["keep", "remove"]
        )
        
        updated = resource.remove_tag("remove")
        
        assert len(resource.tags) == 2  # Original unchanged
        assert len(updated.tags) == 1
        assert "keep" in updated.tags
        assert "remove" not in updated.tags

    def test_update_tags(self):
        """Test updating all tags."""
        resource = Resource.create_new(
            title="Test",
            content="Content",
            category=PARACategory.RESOURCE,
            tags=["old1", "old2"]
        )
        
        updated = resource.update_tags(["new1", "new2", "new3"])
        
        assert len(resource.tags) == 2  # Original unchanged
        assert len(updated.tags) == 3
        assert "new1" in updated.tags
        assert "old1" not in updated.tags

    def test_set_deadline(self):
        """Test setting deadline."""
        resource = Resource.create_new(
            title="Test",
            content="Content",
            category=PARACategory.PROJECT
        )
        
        deadline = datetime.utcnow() + timedelta(days=7)
        updated = resource.set_deadline(deadline)
        
        assert resource.deadline is None  # Original unchanged
        assert updated.deadline == deadline

    def test_set_deadline_archived_future_raises_error(self):
        """Test setting future deadline on archived resource raises error."""
        resource = Resource.create_new(
            title="Test",
            content="Content",
            category=PARACategory.ARCHIVE
        )
        
        future_deadline = datetime.utcnow() + timedelta(days=7)
        with pytest.raises(ValueError, match="Cannot set future deadline"):
            resource.set_deadline(future_deadline)

    def test_set_deadline_archived_past_allowed(self):
        """Test setting past deadline on archived resource is allowed."""
        resource = Resource.create_new(
            title="Test",
            content="Content",
            category=PARACategory.ARCHIVE
        )
        
        past_deadline = datetime.utcnow() - timedelta(days=7)
        updated = resource.set_deadline(past_deadline)
        
        assert updated.deadline == past_deadline

    def test_archive(self):
        """Test archiving a resource."""
        resource = Resource.create_new(
            title="Test",
            content="Content",
            category=PARACategory.PROJECT
        )
        
        archived = resource.archive()
        
        assert resource.category == PARACategory.PROJECT  # Original unchanged
        assert archived.category == PARACategory.ARCHIVE
        assert archived.updated_date > resource.updated_date

    def test_is_active(self):
        """Test active status detection."""
        project = Resource.create_new("Test", "Content", PARACategory.PROJECT)
        area = Resource.create_new("Test", "Content", PARACategory.AREA)
        resource = Resource.create_new("Test", "Content", PARACategory.RESOURCE)
        archive = Resource.create_new("Test", "Content", PARACategory.ARCHIVE)
        
        assert project.is_active()
        assert area.is_active()
        assert resource.is_active()
        assert not archive.is_active()

    def test_is_overdue(self):
        """Test overdue detection."""
        past_deadline = datetime.utcnow() - timedelta(days=1)
        future_deadline = datetime.utcnow() + timedelta(days=1)
        
        no_deadline = Resource.create_new("Test", "Content", PARACategory.PROJECT)
        overdue = Resource.create_new(
            "Test", "Content", PARACategory.PROJECT, deadline=past_deadline
        )
        not_overdue = Resource.create_new(
            "Test", "Content", PARACategory.PROJECT, deadline=future_deadline
        )
        
        assert not no_deadline.is_overdue()
        assert overdue.is_overdue()
        assert not not_overdue.is_overdue()

    def test_days_until_deadline(self):
        """Test days until deadline calculation."""
        future_deadline = datetime.utcnow() + timedelta(days=5)
        past_deadline = datetime.utcnow() - timedelta(days=3)
        
        no_deadline = Resource.create_new("Test", "Content", PARACategory.PROJECT)
        future_resource = Resource.create_new(
            "Test", "Content", PARACategory.PROJECT, deadline=future_deadline
        )
        past_resource = Resource.create_new(
            "Test", "Content", PARACategory.PROJECT, deadline=past_deadline
        )
        
        assert no_deadline.days_until_deadline() is None
        assert future_resource.days_until_deadline() >= 4  # Allow for timing differences
        assert past_resource.days_until_deadline() <= -2

    def test_has_source_thought(self):
        """Test source thought detection."""
        no_source = Resource.create_new("Test", "Content", PARACategory.RESOURCE)
        with_source = Resource.create_new(
            "Test", "Content", PARACategory.RESOURCE,
            source_thought=ThoughtId.generate()
        )
        
        assert not no_source.has_source_thought()
        assert with_source.has_source_thought()

    def test_get_content_preview(self):
        """Test content preview generation."""
        long_content = "A" * 200
        resource = Resource.create_new(
            title="Test",
            content=long_content,
            category=PARACategory.RESOURCE
        )
        
        preview = resource.get_content_preview(50)
        assert len(preview) <= 50
        assert preview.endswith("...")

    def test_validation_errors(self):
        """Test various validation errors during creation."""
        # Test type validations
        with pytest.raises(TypeError, match="Title must be a string"):
            Resource(
                id=ResourceId.generate(),
                title=123,
                content=ContentText.create("test"),
                category=PARACategory.PROJECT,
                tags=ResourceTags.empty(),
                source_thought=None,
                created_date=datetime.utcnow(),
                updated_date=datetime.utcnow()
            )

    def test_business_rule_validation(self):
        """Test business rule validation."""
        # Test updated_date before created_date
        created = datetime.utcnow()
        updated = created - timedelta(hours=1)
        
        with pytest.raises(ValueError, match="Updated date cannot be before created date"):
            Resource(
                id=ResourceId.generate(),
                title="Test",
                content=ContentText.create("content"),
                category=PARACategory.PROJECT,
                tags=ResourceTags.empty(),
                source_thought=None,
                created_date=created,
                updated_date=updated
            )

    def test_string_representations(self):
        """Test string representations."""
        resource = Resource.create_new(
            title="Test Resource",
            content="Content",
            category=PARACategory.PROJECT
        )
        
        str_repr = str(resource)
        assert "Test Resource" in str_repr
        assert "PROJECT" in str_repr or "project" in str_repr
        
        detailed_repr = repr(resource)
        assert "Resource(" in detailed_repr
        assert "Test Resource" in detailed_repr

    def test_immutability(self):
        """Test that Resource is immutable."""
        resource = Resource.create_new(
            title="Test",
            content="Content",
            category=PARACategory.PROJECT
        )
        
        # Updating should return new instance
        updated = resource.update_content("New content")
        assert resource is not updated
        assert str(resource.content) == "Content"
        assert str(updated.content) == "New content"