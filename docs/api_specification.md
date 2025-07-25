# API Specification (Planned)

This document outlines the planned REST API for ParaFlow's thought streaming and PARA management capabilities.

## Overview

The ParaFlow API will provide endpoints for:
- Thought capture and streaming
- PARA framework management
- Claude integration for processing
- Real-time status updates
- Content organization

## Base URL

```
https://api.paraflow.dev/v1
```

## Authentication

```http
Authorization: Bearer <api_key>
```

## Endpoints

### Thought Management

#### Create Thought
```http
POST /thoughts
Content-Type: application/json

{
  "title": "Project idea",
  "content": "Build an AI-powered personal assistant for PARA",
  "project_tag": "ParaFlow",
  "area_tag": "Software Development"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Project idea",
  "content": "Build an AI-powered personal assistant for PARA",
  "created_date": "2025-07-19T07:22:57Z",
  "processed": false,
  "processing_status": "new",
  "project_tag": "ParaFlow",
  "area_tag": "Software Development"
}
```

#### Get Thought
```http
GET /thoughts/{id}
```

#### Update Thought Status
```http
PATCH /thoughts/{id}/status
Content-Type: application/json

{
  "status": "processing"
}
```

#### List Thoughts
```http
GET /thoughts?status=new&project_tag=ParaFlow&limit=10&offset=0
```

### Processing

#### Trigger Processing
```http
POST /thoughts/{id}/process
```

#### Get Processing Status
```http
GET /thoughts/{id}/processing
```

### PARA Management

#### Get PARA Categories
```http
GET /para/categories
```

#### Move to Category
```http
POST /thoughts/{id}/categorize
Content-Type: application/json

{
  "category": "projects",
  "subcategory": "active"
}
```

### Webhooks

#### Register Webhook
```http
POST /webhooks
Content-Type: application/json

{
  "url": "https://example.com/webhook",
  "events": ["thought.created", "thought.processed"],
  "secret": "webhook_secret"
}
```

## Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Rate Limiting

- 1000 requests per hour per API key
- 10 requests per second burst limit

## Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title cannot be empty",
    "details": {
      "field": "title",
      "constraint": "required"
    }
  }
}
```

## Planned Features

### Real-time Updates
- WebSocket connections for live status updates
- Server-sent events for processing notifications

### Batch Operations
- Bulk thought creation
- Batch status updates
- Mass categorization

### Advanced Search
- Full-text search across thoughts
- Filtering by multiple criteria
- Faceted search results

### Integration APIs
- Notion workspace sync
- Export/import functionality
- Third-party platform connectors

*Note: This API specification is planned for future implementation. The current release focuses on the domain model foundation.*