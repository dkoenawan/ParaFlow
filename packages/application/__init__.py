"""
ParaFlow Application Package

This package contains the application layer that orchestrates domain services
and coordinates between the domain layer and infrastructure adapters.

Following hexagonal architecture principles, this layer:
- Contains use cases and application services
- Orchestrates domain services
- Handles transaction boundaries
- Manages application-specific logic

Modules:
- use_cases: Application use cases and orchestration logic
- handlers: Event and command handlers
- config: Application configuration and dependency injection
"""

__version__ = "0.1.0"
__all__ = ["use_cases", "handlers", "config"]