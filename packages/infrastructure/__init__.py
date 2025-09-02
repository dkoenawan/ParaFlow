"""
ParaFlow Infrastructure Package

This package contains the infrastructure layer that implements the secondary
ports defined in the domain layer. It handles all external concerns and
technical details.

Following hexagonal architecture principles, this layer:
- Implements secondary ports (driven adapters)
- Handles data persistence
- Manages external service integrations
- Provides technical infrastructure services

Modules:
- repositories: Data access implementations
- external: External service integrations
- events: Event infrastructure and messaging
- adapters: Secondary adapter implementations
"""

__version__ = "0.1.0"
__all__ = ["repositories", "external", "events", "adapters"]