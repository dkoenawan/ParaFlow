"""ThoughtId value object for type-safe thought identification."""

import uuid
from typing import Union
from dataclasses import dataclass


@dataclass(frozen=True)
class ThoughtId:
    """Value object representing a unique thought identifier.
    
    Provides type safety and validation for thought IDs using UUID.
    Immutable to prevent accidental modification.
    """
    
    value: uuid.UUID

    def __post_init__(self) -> None:
        """Validate the UUID value after initialization."""
        if not isinstance(self.value, uuid.UUID):
            raise TypeError(f"ThoughtId must be a UUID, got {type(self.value)}")

    @classmethod
    def generate(cls) -> "ThoughtId":
        """Generate a new random ThoughtId.
        
        Returns:
            A new ThoughtId with a randomly generated UUID
        """
        return cls(uuid.uuid4())

    @classmethod
    def from_string(cls, id_string: str) -> "ThoughtId":
        """Create a ThoughtId from a string representation.
        
        Args:
            id_string: String representation of a UUID
            
        Returns:
            ThoughtId object
            
        Raises:
            ValueError: If the string is not a valid UUID
        """
        try:
            return cls(uuid.UUID(id_string))
        except ValueError as e:
            raise ValueError(f"Invalid UUID string: {id_string}") from e

    @classmethod
    def from_uuid(cls, uuid_obj: uuid.UUID) -> "ThoughtId":
        """Create a ThoughtId from a UUID object.
        
        Args:
            uuid_obj: UUID object
            
        Returns:
            ThoughtId object
        """
        return cls(uuid_obj)

    def __str__(self) -> str:
        """Return string representation of the ThoughtId."""
        return str(self.value)

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return f"ThoughtId('{self.value}')"

    def __eq__(self, other: object) -> bool:
        """Compare ThoughtIds for equality."""
        if not isinstance(other, ThoughtId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        """Return hash of the UUID for use in sets and dicts."""
        return hash(self.value)