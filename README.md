# ParaFlow

AI-powered personal assistant that captures, processes, and organizes your thoughts into the PARA framework using clean hexagonal architecture.

## 🎯 Current Status: Notion API MVP Complete

The project now features a complete Notion API integration MVP that demonstrates all CRUD operations using hexagonal architecture principles. This implementation serves as the foundation for building the full PARA framework.

**Key Features Implemented:**
- ✅ Complete CRUD operations for Notion pages
- ✅ Hexagonal architecture with ports and adapters
- ✅ Comprehensive test suite (49 total tests: 38 unit tests + 11 integration tests)
- ✅ Authentication and configuration management
- ✅ Error handling and validation
- ✅ Demo script for quick verification

## 🏗️ Architecture Overview

ParaFlow follows hexagonal architecture (ports and adapters pattern) to ensure clean separation of concerns and technology independence:

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Create Page   │  │   Update Page   │  │  List Pages  │ │
│  │   Use Case     │  │   Use Case     │  │   Use Case   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│          Domain Layer   │                                   │
│  ┌─────────────────┐   │       ┌─────────────────────────┐ │
│  │     Page        │   │       │ PageRepositoryPort      │ │
│  │   Entity        │   │       │   (Interface)          │ │
│  └─────────────────┘   │       └─────────────────────────┘ │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│   Infrastructure Layer  │                                   │
│  ┌─────────────────────┐│   ┌─────────────────────────────┐ │
│  │ NotionPageRepository││   │  AuthenticationAdapter      │ │
│  │      Adapter        ││   │                             │ │
│  └─────────────────────┘│   └─────────────────────────────┘ │
└─────────────────────────┼───────────────────────────────────┘
                          │
                    ┌─────▼─────┐
                    │  Notion   │
                    │    API    │
                    └───────────┘
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ParaFlow.git
cd ParaFlow

# Copy the example environment file
cp .env.example .env

# Edit .env with your Notion credentials
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_page_id
```

### 2. Install Dependencies

```bash
# Install required packages
pip install notion-client python-dotenv pytest-asyncio

# Or if using virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install notion-client python-dotenv pytest-asyncio
```

### 3. Configure Notion Integration

1. **Create Integration**:
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Name your integration and select workspace
   - Copy the "Internal Integration Token"

2. **Share a Page**:
   - Open any page in Notion
   - Click "Share" → "Invite"
   - Add your integration
   - Copy the page ID from URL

3. **Update .env**:
   - Add your token and page ID to .env file

### 4. Run the Demo

```bash
# Execute the demonstration script
python examples/demo_script.py
```

## 📁 Project Structure

```
ParaFlow/
├── packages/                    # Main application code
│   ├── domain/                  # Business logic (technology-agnostic)
│   │   ├── models/
│   │   │   └── page.py         # Page domain entity
│   │   ├── ports/
│   │   │   └── page_repository.py  # Repository interface
│   │   └── exceptions.py       # Domain-specific exceptions
│   │
│   ├── application/             # Use cases and orchestration
│   │   └── use_cases/
│   │       └── page_operations.py  # CRUD use cases
│   │
│   └── infrastructure/          # External integrations
│       └── adapters/
│           ├── auth.py         # Authentication handling
│           └── notion_adapter.py   # Notion API implementation
│
├── tests/                       # Comprehensive test suite
│   ├── unit/                   # Isolated unit tests (38 tests)
│   └── integration/            # End-to-end tests
│
├── examples/
│   └── demo_script.py          # Complete usage demonstration
│
├── README_NOTION_MVP.md        # Detailed technical documentation
├── .env.example               # Configuration template
└── README.md                  # This file
```

## ⚡ Features

### CRUD Operations
- **Create Page**: Create new pages with title and content
- **Read Page**: Retrieve pages by ID with full metadata
- **Update Page**: Modify existing page title and content
- **Delete Page**: Remove pages (archives in Notion)
- **List Pages**: Paginated page listing with search
- **Page Existence**: Check if page exists

### Technical Features
- **Hexagonal Architecture**: Clean separation of concerns
- **Async/Await Support**: Full asynchronous operation support
- **Type Safety**: Complete type hints throughout codebase
- **Error Handling**: Comprehensive domain-specific exceptions
- **Input Validation**: Robust validation at all layers
- **Immutable Entities**: Frozen dataclasses for data integrity

### Testing & Quality
- **49 Total Tests**: 38 unit tests + 11 integration tests for comprehensive coverage
- **Integration Tests**: End-to-end validation framework
- **Clean Code**: PEP 8 compliance, docstrings, type hints
- **Architecture Validation**: Proper dependency inversion

## 🧪 Testing

```bash
# Run unit tests (requires pytest installation)
python -m pytest tests/unit/ -v

# Run with coverage (requires pytest-cov)
python -m pytest tests/unit/ --cov=packages --cov-report=html

# Run integration tests (requires Notion setup)
python -m pytest tests/integration/ -v
```

## 📖 Usage Examples

### Basic CRUD Operations

```python
import asyncio
from packages.infrastructure.adapters.auth import AuthenticationAdapter
from packages.infrastructure.adapters.notion_adapter import NotionPageRepositoryAdapter
from packages.application.use_cases.page_operations import PageApplicationService

async def example():
    # Initialize services
    auth = AuthenticationAdapter()
    adapter = NotionPageRepositoryAdapter(auth)
    service = PageApplicationService(adapter)
    
    # Create a page
    page = await service.create_page(
        title="My PARA Framework Page",
        content="This page demonstrates the MVP implementation",
        metadata={"category": "projects"}
    )
    
    # Read the page
    retrieved = await service.get_page(page.id)
    
    # Update the page
    updated = await service.update_page(
        page.id,
        title="Updated Title",
        content="Updated content with new information"
    )
    
    # Delete the page
    deleted = await service.delete_page(page.id)

asyncio.run(example())
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NOTION_TOKEN` | Yes | Notion integration token from your integration |
| `NOTION_DATABASE_ID` | Yes | ID of a Notion page shared with your integration |
| `ENVIRONMENT` | No | Environment indicator (development/production) |

## 🛣️ Roadmap

### Phase 1: MVP Foundation ✅ COMPLETE
- [x] Notion API integration
- [x] Basic CRUD operations
- [x] Hexagonal architecture implementation
- [x] Comprehensive testing
- [x] Documentation and examples

### Phase 2: PARA Framework Core (Next)
- [ ] PARA domain models (Projects, Areas, Resources, Archives)
- [ ] Classification engine for organizing information
- [ ] PARA methodology workflows
- [ ] Advanced search and filtering

### Phase 3: Multi-Storage Support
- [ ] Excel adapter implementation
- [ ] Google Sheets integration
- [ ] File system adapter
- [ ] Database storage options

### Phase 4: User Interface
- [ ] Command-line interface (CLI)
- [ ] Web-based dashboard
- [ ] API endpoints for external integrations

### Phase 5: AI Enhancement
- [ ] Intelligent content classification
- [ ] Natural language processing
- [ ] Automated organization suggestions
- [ ] Content summarization and insights

## 🤝 Contributing

This project follows clean architecture principles and test-driven development:

1. Keep domain layer technology-agnostic
2. Use ports for all external dependencies
3. Write tests for all new functionality
4. Follow existing patterns and conventions
5. Maintain comprehensive documentation

## 📄 Documentation

- **[Technical Documentation](README_NOTION_MVP.md)**: Detailed architecture and implementation guide
- **[API Documentation](packages/)**: Inline code documentation with docstrings
- **[Demo Script](examples/demo_script.py)**: Complete usage examples
- **[Configuration Guide](.env.example)**: Environment setup instructions

## 📊 Implementation Metrics

- **Architecture**: Hexagonal (Ports & Adapters)
- **Lines of Code**: ~2,000 lines of implementation
- **Test Coverage**: 49 comprehensive tests (38 unit + 11 integration)
- **Dependencies**: 3 production dependencies
- **Features**: 6 core CRUD operations
- **Documentation**: Complete with examples and guides

---

**Status**: ✅ Notion API MVP Complete and Production Ready  
**Architecture**: ✅ Hexagonal Architecture Compliant  
**Tests**: ✅ 49/49 Tests Implemented (Unit + Integration)  
**Next Phase**: PARA Framework Domain Implementation

