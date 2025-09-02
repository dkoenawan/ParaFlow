"""
ParaFlow Interfaces Package

This package contains the primary adapters (driving adapters) that handle
external requests and translate them into application use cases. These
interfaces provide different ways to interact with the system.

Following hexagonal architecture principles, this layer:
- Implements primary ports (driving adapters)
- Handles external protocol concerns (HTTP, CLI, webhooks)
- Translates external requests to application use cases
- Formats responses for external systems

Modules:
- api: REST API and web service interfaces
- webhooks: Webhook handlers and event receivers
- cli: Command-line interface implementations
"""

__version__ = "0.1.0"
__all__ = ["api", "webhooks", "cli"]