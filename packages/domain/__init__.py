"""
ParaFlow Domain Package

This package contains the core business logic and domain models for ParaFlow.
Following hexagonal architecture principles, this layer is independent of
external concerns and contains only pure business rules.

Modules:
- models: Domain entities and value objects
- services: Domain services containing business logic
- ports: Primary and secondary port interfaces
"""

__version__ = "0.1.0"
__all__ = ["models", "services", "ports"]