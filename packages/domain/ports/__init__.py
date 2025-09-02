"""
Domain Ports Package

Contains port interfaces that define the contracts between the domain layer
and external concerns. Following hexagonal architecture principles:

- Primary ports: Interfaces for driving adapters (API, CLI, etc.)
- Secondary ports: Interfaces for driven adapters (databases, external services)

These ports enable dependency inversion and keep the domain layer independent
of infrastructure concerns.
"""

__all__ = []