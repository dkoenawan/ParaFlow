"""Tests for ThoughtId value object."""

import uuid
import pytest
from packages.domain.models.thought_id import ThoughtId


class TestThoughtId:
    """Test cases for ThoughtId value object."""

    def test_create_with_uuid(self) -> None:
        """Test creating ThoughtId with a UUID."""
        test_uuid = uuid.uuid4()
        thought_id = ThoughtId(test_uuid)
        
        assert thought_id.value == test_uuid
        assert isinstance(thought_id.value, uuid.UUID)

    def test_generate_creates_unique_ids(self) -> None:
        """Test that generate() creates unique ThoughtIds."""
        id1 = ThoughtId.generate()
        id2 = ThoughtId.generate()
        
        assert id1 != id2
        assert isinstance(id1.value, uuid.UUID)
        assert isinstance(id2.value, uuid.UUID)

    def test_from_string_valid_uuid(self) -> None:
        """Test creating ThoughtId from valid UUID string."""
        uuid_string = "123e4567-e89b-12d3-a456-426614174000"
        thought_id = ThoughtId.from_string(uuid_string)
        
        assert str(thought_id.value) == uuid_string
        assert isinstance(thought_id.value, uuid.UUID)

    def test_from_string_invalid_uuid(self) -> None:
        """Test that invalid UUID string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID string"):
            ThoughtId.from_string("not-a-uuid")

    def test_from_uuid_object(self) -> None:
        """Test creating ThoughtId from UUID object."""
        test_uuid = uuid.uuid4()
        thought_id = ThoughtId.from_uuid(test_uuid)
        
        assert thought_id.value == test_uuid

    def test_string_representation(self) -> None:
        """Test string representation of ThoughtId."""
        test_uuid = uuid.uuid4()
        thought_id = ThoughtId(test_uuid)
        
        assert str(thought_id) == str(test_uuid)

    def test_repr_representation(self) -> None:
        """Test repr representation of ThoughtId."""
        test_uuid = uuid.uuid4()
        thought_id = ThoughtId(test_uuid)
        
        expected = f"ThoughtId('{test_uuid}')"
        assert repr(thought_id) == expected

    def test_equality(self) -> None:
        """Test equality comparison between ThoughtIds."""
        test_uuid = uuid.uuid4()
        id1 = ThoughtId(test_uuid)
        id2 = ThoughtId(test_uuid)
        id3 = ThoughtId(uuid.uuid4())
        
        assert id1 == id2
        assert id1 != id3
        assert id2 != id3

    def test_equality_with_different_type(self) -> None:
        """Test equality comparison with different types."""
        thought_id = ThoughtId.generate()
        
        assert thought_id != "not-a-thought-id"
        assert thought_id != 123
        assert thought_id != thought_id.value  # Not equal to raw UUID

    def test_hash_consistency(self) -> None:
        """Test that equal ThoughtIds have the same hash."""
        test_uuid = uuid.uuid4()
        id1 = ThoughtId(test_uuid)
        id2 = ThoughtId(test_uuid)
        
        assert hash(id1) == hash(id2)

    def test_hash_different_for_different_ids(self) -> None:
        """Test that different ThoughtIds have different hashes."""
        id1 = ThoughtId.generate()
        id2 = ThoughtId.generate()
        
        # Note: Hash collisions are possible but extremely unlikely with UUIDs
        assert hash(id1) != hash(id2)

    def test_can_be_used_as_dict_key(self) -> None:
        """Test that ThoughtId can be used as dictionary key."""
        id1 = ThoughtId.generate()
        id2 = ThoughtId.generate()
        
        test_dict = {id1: "value1", id2: "value2"}
        
        assert test_dict[id1] == "value1"
        assert test_dict[id2] == "value2"

    def test_can_be_used_in_set(self) -> None:
        """Test that ThoughtId can be used in sets."""
        id1 = ThoughtId.generate()
        id2 = ThoughtId.generate()
        
        test_set = {id1, id2}
        
        assert len(test_set) == 2
        assert id1 in test_set
        assert id2 in test_set

    def test_immutability(self) -> None:
        """Test that ThoughtId is immutable (frozen dataclass)."""
        thought_id = ThoughtId.generate()
        
        with pytest.raises(Exception):  # dataclass.FrozenInstanceError in Python 3.7+
            thought_id.value = uuid.uuid4()  # type: ignore

    def test_type_validation_in_post_init(self) -> None:
        """Test that __post_init__ validates the UUID type."""
        with pytest.raises(TypeError, match="ThoughtId must be a UUID"):
            ThoughtId("not-a-uuid")  # type: ignore