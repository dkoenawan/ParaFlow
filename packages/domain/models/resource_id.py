"""ResourceId value object for type-safe resource identification."""

import uuid
from typing import Union
from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceId:
    """Value object representing a unique resource identifier.
    
    Provides type safety and validation for resource IDs using UUID.
    Immutable to prevent accidental modification.
    """
    
    value: uuid.UUID

    def __post_init__(self) -> None:
        """Validate the UUID value after initialization."""
        if not isinstance(self.value, uuid.UUID):
            raise TypeError(f"ResourceId must be a UUID, got {type(self.value)}")

    @classmethod
    def generate(cls) -> "ResourceId":
        """Generate a new random ResourceId.
        
        Returns:
            A new ResourceId with a randomly generated UUID
        """
        return cls(uuid.uuid4())

    @classmethod
    def from_string(cls, id_string: str) -> "ResourceId":
        """Create a ResourceId from a string representation.
        
        Args:
            id_string: String representation of a UUID
            
        Returns:
            ResourceId object
            
        Raises:
            ValueError: If the string is not a valid UUID
        """
        try:
            return cls(uuid.UUID(id_string))
        except ValueError as e:
            raise ValueError(f"Invalid UUID string: {id_string}") from e

    @classmethod
    def from_uuid(cls, uuid_obj: uuid.UUID) -> "ResourceId":
        """Create a ResourceId from a UUID object.
        
        Args:
            uuid_obj: UUID object
            
        Returns:
            ResourceId object
        """
        return cls(uuid_obj)

    def __str__(self) -> str:
        """Return string representation of the ResourceId."""
        return str(self.value)

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return f"ResourceId('{self.value}')"

    def __eq__(self, other: object) -> bool:
        """Compare ResourceIds for equality."""
        if not isinstance(other, ResourceId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        """Return hash of the UUID for use in sets and dicts."""
        return hash(self.value)