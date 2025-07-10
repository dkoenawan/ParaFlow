# Architecture Discussion Summary

## Project Vision
ParaFlow is an AI-powered automation tool for organizing personal life using the PARA methodology. While initially designed for Notion integration, it's built to be extensible for other platforms and use cases.

## Key Architecture Decisions

### 1. Ports/Adapters Architecture
- **Core Domain**: Pure business logic for PARA categorization and organization
- **Ports**: Clean interfaces defining contracts between core and external systems  
- **Adapters**: Platform-specific implementations (Notion, Obsidian, etc.)

### 2. Technology Stack
- **Language**: Python
- **Deployment**: Docker containers
- **AI Integration**: Claude Code for action execution

### 3. AI Integration Strategy
**Role of Claude Code**: Action executor, not just analyzer
- Python app handles orchestration, webhooks, PARA categorization logic
- Claude Code executes actual API calls, file operations, system interactions
- Communication via HTTP between services

**Example Workflow**:
1. New entry added → webhook received
2. Python app processes content and determines actions needed
3. Python app sends instructions to Claude Code service
4. Claude Code executes the actual API calls (Notion updates, file operations, etc.)

### 4. Deployment Architecture: Sidecar Pattern
**Chosen Approach**: Docker Compose with separate containers that deploy together
- **Main Container**: Python FastAPI application
- **Sidecar Container**: Claude Code HTTP service
- **Communication**: HTTP requests over shared Docker network
- **Benefits**: 
  - Integrated deployment (ships together)
  - Easy local development and testing
  - Isolated services for debugging
  - Clean separation of concerns

### 5. Local Development Setup
```yaml
# docker-compose.yml
paraflow:          # Main Python app (port 8000)
claude-sidecar:    # Claude Code service (port 8080)
```

**Testing Workflow**:
- `docker-compose up --build` - Start everything
- Direct sidecar testing via curl
- Isolated log viewing per service
- Hot reloading individual services

## Project Structure
```
paraflow/
├── src/domain/           # Core PARA business logic
├── src/adapters/         # Platform integrations
├── src/infrastructure/   # Cross-cutting concerns
├── infrastructure/       # Docker, K8s, Terraform
├── docs/                 # Architecture documentation
└── tests/               # Test files
```

## Next Steps
1. Implement basic Python project structure
2. Create Docker setup for sidecar deployment
3. Build Claude Code HTTP wrapper service
4. Implement core PARA categorization logic
5. Add Notion adapter integration