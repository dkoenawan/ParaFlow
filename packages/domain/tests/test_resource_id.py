"""Tests for ResourceId value object."""

import uuid
import pytest
from packages.domain.models.resource_id import ResourceId


class TestResourceId:
    """Test cases for ResourceId value object."""

    def test_generate_creates_valid_id(self):
        """Test that generate() creates a valid ResourceId with UUID."""
        resource_id = ResourceId.generate()
        
        assert isinstance(resource_id, ResourceId)
        assert isinstance(resource_id.value, uuid.UUID)

    def test_generate_creates_unique_ids(self):
        """Test that generate() creates unique IDs."""
        id1 = ResourceId.generate()
        id2 = ResourceId.generate()
        
        assert id1 != id2
        assert id1.value != id2.value

    def test_from_string_valid_uuid(self):
        """Test creating ResourceId from valid UUID string."""
        uuid_str = "12345678-1234-5678-9012-123456789012"
        resource_id = ResourceId.from_string(uuid_str)
        
        assert isinstance(resource_id, ResourceId)
        assert str(resource_id.value) == uuid_str

    def test_from_string_invalid_uuid(self):
        """Test that invalid UUID strings raise ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID string"):
            ResourceId.from_string("not-a-uuid")
        
        with pytest.raises(ValueError, match="Invalid UUID string"):
            ResourceId.from_string("")

    def test_from_uuid_object(self):
        """Test creating ResourceId from UUID object."""
        uuid_obj = uuid.uuid4()
        resource_id = ResourceId.from_uuid(uuid_obj)
        
        assert isinstance(resource_id, ResourceId)
        assert resource_id.value == uuid_obj

    def test_invalid_type_raises_error(self):
        """Test that invalid types raise TypeError."""
        with pytest.raises(TypeError, match="ResourceId must be a UUID"):
            ResourceId("not-a-uuid")

    def test_string_representation(self):
        """Test string representation of ResourceId."""
        uuid_str = "12345678-1234-5678-9012-123456789012"
        resource_id = ResourceId.from_string(uuid_str)
        
        assert str(resource_id) == uuid_str

    def test_repr(self):
        """Test detailed string representation."""
        uuid_str = "12345678-1234-5678-9012-123456789012"
        resource_id = ResourceId.from_string(uuid_str)
        expected = f"ResourceId('{uuid_str}')"
        
        assert repr(resource_id) == expected

    def test_equality(self):
        """Test equality comparison between ResourceIds."""
        uuid_str = "12345678-1234-5678-9012-123456789012"
        id1 = ResourceId.from_string(uuid_str)
        id2 = ResourceId.from_string(uuid_str)
        id3 = ResourceId.generate()
        
        assert id1 == id2
        assert id1 != id3
        assert id1 != "not-a-resource-id"

    def test_hash_consistency(self):
        """Test that equal ResourceIds have equal hashes."""
        uuid_str = "12345678-1234-5678-9012-123456789012"
        id1 = ResourceId.from_string(uuid_str)
        id2 = ResourceId.from_string(uuid_str)
        
        assert hash(id1) == hash(id2)

    def test_hash_uniqueness(self):
        """Test that different ResourceIds have different hashes."""
        id1 = ResourceId.generate()
        id2 = ResourceId.generate()
        
        # Note: Hash collisions are possible but extremely unlikely with UUIDs
        assert hash(id1) != hash(id2)

    def test_can_be_used_as_dict_key(self):
        """Test that ResourceId can be used as dictionary key."""
        resource_id = ResourceId.generate()
        test_dict = {resource_id: "test_value"}
        
        assert test_dict[resource_id] == "test_value"

    def test_can_be_used_in_set(self):
        """Test that ResourceId can be used in sets."""
        id1 = ResourceId.generate()
        id2 = ResourceId.generate()
        
        resource_set = {id1, id2}
        assert len(resource_set) == 2
        assert id1 in resource_set
        assert id2 in resource_set