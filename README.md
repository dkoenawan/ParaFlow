# ParaFlow
AI-powered personal assistant that captures, processes, and organizes your thoughts into the PARA framework

## Overview

ParaFlow helps you maintain an organized PARA (Projects, Areas, Resources, Archives) system by automatically scanning, updating, and reorganizing your content. While initially designed for Notion integration, ParaFlow is built to be extensible for other platforms and use cases.

## What is PARA?

PARA is a productivity method that organizes information into four categories:
- **Projects**: Things with a deadline and specific outcome
- **Areas**: Ongoing responsibilities to maintain
- **Resources**: Topics of ongoing interest
- **Archives**: Inactive items from the other three categories

## The Challenge

Maintaining a PARA system requires constant manual updates:
- Moving completed projects to archives
- Reorganizing resources as interests evolve
- Keeping area documentation current
- Ensuring easy access to relevant information

## The Solution

ParaFlow automates this process by:
- Scanning your workspace for content changes
- Receiving webhooks for real-time updates
- Automatically categorizing and reorganizing content
- Maintaining consistent structure across your PARA system
- Providing organic ways to update and extract information

## Features (Planned)

- **Automated Scanning**: Periodically scans your workspace for changes
- **Webhook Integration**: Receives real-time updates
- **Intelligent Categorization**: Automatically moves content between PARA categories
- **Smart Organization**: Maintains consistent structure and naming conventions
- **Easy Information Extraction**: Provides streamlined access to your organized content
- **Deployable**: Can be deployed as a service to run continuously
- **Extensible**: Built to support multiple platforms beyond Notion

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/dkoenawan/ParaFlow.git
cd ParaFlow

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest packages/domain/tests/

# Run type checking
mypy packages/
```

### Current Implementation Status

**✅ Completed:**
- Core domain model for thought streaming
- ThoughtContent entity with immutable design
- Processing status lifecycle management
- Type-safe value objects (ThoughtId, ContentText)
- Comprehensive test suite (76+ tests)
- Monorepo package structure

**🚧 In Progress:**
- Infrastructure layer implementation
- API endpoints for thought capture
- Claude integration for content processing

**📋 Planned:**
- PARA framework categorization
- Notion integration
- Webhook support
- Automated content scanning

## Architecture

ParaFlow follows hexagonal architecture (Ports & Adapters) and domain-driven design principles:

### Domain Model

The core domain model includes:

- **`ThoughtContent`**: Main entity representing user thoughts with free-form content
- **`ThoughtId`**: Type-safe unique identifier for thoughts  
- **`ContentText`**: Value object for validated thought content
- **`ProcessingStatus`**: Enum managing thought processing lifecycle (NEW → PROCESSING → COMPLETED/FAILED)

Key design principles:
- **Immutable entities**: All domain objects are frozen dataclasses
- **Type safety**: Strong typing with native Python union types
- **Business rules**: Domain logic enforced at entity level
- **No length limits**: Supports seamless thought streaming

### Package Structure

```
packages/
├── domain/                 # Core domain layer
│   ├── models/            # Domain entities and value objects
│   └── tests/             # Comprehensive test suite
├── infrastructure/        # External integrations (planned)
└── application/          # Use cases and services (planned)
```

## Contributing

This is an open source project under the Apache 2.0 license. Contributors are welcome to adapt and extend ParaFlow for their own platforms and use cases.

## License

Apache 2.0 - see LICENSE file for details
