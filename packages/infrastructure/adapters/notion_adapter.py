"""
Notion API adapter implementation.

This module implements the PageRepositoryPort interface using the Notion API.
It handles all Notion-specific operations including authentication, API calls,
and data mapping between domain entities and Notion API formats.
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from notion_client import Client as NotionClient
from notion_client.errors import HTTPResponseError, APIResponseError, RequestTimeoutError

from ...domain.models.page import Page
from ...domain.models.database import Database
from ...domain.models.database_property import DatabaseProperty
from ...domain.models.property_types import PropertyType
from ...domain.ports.page_repository import PageRepositoryPort
from ...domain.exceptions import (
    PageCreationError,
    PageUpdateError,
    PageDeletionError,
    PageRetrievalError,
    PageNotFoundError,
    ValidationError
)
from .auth import AuthenticationAdapter


class NotionPageRepositoryAdapter(PageRepositoryPort):
    """
    Notion API implementation of the PageRepositoryPort interface.
    
    This adapter translates between the domain's Page entity and Notion's
    API format, handling all Notion-specific operations while maintaining
    the interface contract defined by the port.
    """
    
    def __init__(self, auth_adapter: Optional[AuthenticationAdapter] = None):
        """
        Initialize the Notion adapter.
        
        Args:
            auth_adapter: Authentication adapter for credential management.
                         If None, creates a new instance.
        """
        self.auth_adapter = auth_adapter or AuthenticationAdapter()
        self.auth_adapter.validate_configuration()
        
        # Initialize Notion client
        token = self.auth_adapter.get_notion_token()
        self.client = NotionClient(auth=token)
    
    async def create_page(self, page: Page) -> Page:
        """
        Create a new page in Notion.

        Supports creating both standalone pages and database pages.
        For database pages, set metadata['parent_database_id'] and metadata['properties'].

        Args:
            page: Page entity to create

        Returns:
            Created page with Notion ID

        Raises:
            PageCreationError: If page creation fails
            ValidationError: If page data is invalid
        """
        try:
            if page.has_id():
                raise ValidationError("Page already has an ID. Use update_page instead.")

            if page.is_empty():
                raise ValidationError("Page must have either title or content.")

            # Check if this is a database page
            parent_database_id = page.metadata.get("parent_database_id") if page.metadata else None

            if parent_database_id:
                # Creating page in a database
                properties = self._build_database_page_properties(page)
                parent = {"type": "database_id", "database_id": parent_database_id}
            else:
                # Creating standalone page
                properties = self._build_page_properties(page)
                parent = {"type": "page_id", "page_id": self._get_parent_page_id()}

            # Create page content (children blocks)
            children = self._build_page_children(page)

            # Make API call to create page
            response = await self._run_sync(
                self.client.pages.create,
                parent=parent,
                properties=properties,
                children=children
            )

            return self._map_notion_response_to_page(response)

        except (HTTPResponseError, APIResponseError, RequestTimeoutError) as e:
            raise PageCreationError(f"Failed to create page in Notion: {str(e)}")
        except Exception as e:
            raise PageCreationError(f"Unexpected error during page creation: {str(e)}")
    
    async def get_page_by_id(self, page_id: str) -> Optional[Page]:
        """
        Retrieve a page from Notion by ID.
        
        Args:
            page_id: Notion page ID
            
        Returns:
            Page entity if found, None if not found
            
        Raises:
            PageRetrievalError: If retrieval operation fails
        """
        try:
            # Get page properties
            page_response = await self._run_sync(
                self.client.pages.retrieve,
                page_id=page_id
            )
            
            # Get page content (blocks)
            blocks_response = await self._run_sync(
                self.client.blocks.children.list,
                block_id=page_id
            )
            
            return self._map_notion_page_to_domain(page_response, blocks_response)
            
        except APIResponseError as e:
            if e.status == 404:
                return None
            raise PageRetrievalError(f"Failed to retrieve page from Notion: {str(e)}")
        except (APIConnectionError, RequestTimeoutError) as e:
            raise PageRetrievalError(f"Failed to retrieve page from Notion: {str(e)}")
        except Exception as e:
            raise PageRetrievalError(f"Unexpected error during page retrieval: {str(e)}")
    
    async def update_page(self, page: Page) -> Page:
        """
        Update an existing page in Notion.
        
        Args:
            page: Page entity with updated data (must have ID)
            
        Returns:
            Updated page entity
            
        Raises:
            PageNotFoundError: If page does not exist
            PageUpdateError: If update operation fails
            ValidationError: If page data is invalid
        """
        try:
            if not page.has_id():
                raise ValidationError("Page must have an ID to be updated.")
            
            # Update page properties
            properties = self._build_page_properties(page)
            
            response = await self._run_sync(
                self.client.pages.update,
                page_id=page.id,
                properties=properties
            )
            
            # Update page content if needed
            if page.content.strip():
                await self._update_page_content(page.id, page.content)
            
            # Retrieve updated page to return
            updated_page = await self.get_page_by_id(page.id)
            if updated_page is None:
                raise PageNotFoundError(page.id)
            
            return updated_page
            
        except APIResponseError as e:
            if e.status == 404:
                raise PageNotFoundError(page.id)
            raise PageUpdateError(f"Failed to update page in Notion: {str(e)}")
        except (APIConnectionError, RequestTimeoutError) as e:
            raise PageUpdateError(f"Failed to update page in Notion: {str(e)}")
        except (PageNotFoundError, ValidationError):
            raise
        except Exception as e:
            raise PageUpdateError(f"Unexpected error during page update: {str(e)}")
    
    async def delete_page(self, page_id: str) -> bool:
        """
        Delete a page from Notion (archive it).
        
        Args:
            page_id: Notion page ID
            
        Returns:
            True if page was archived, False if page did not exist
            
        Raises:
            PageDeletionError: If deletion operation fails
        """
        try:
            await self._run_sync(
                self.client.pages.update,
                page_id=page_id,
                archived=True
            )
            return True
            
        except APIResponseError as e:
            if e.status == 404:
                return False
            raise PageDeletionError(f"Failed to delete page in Notion: {str(e)}")
        except (APIConnectionError, RequestTimeoutError) as e:
            raise PageDeletionError(f"Failed to delete page in Notion: {str(e)}")
        except Exception as e:
            raise PageDeletionError(f"Unexpected error during page deletion: {str(e)}")
    
    async def list_pages(self, limit: Optional[int] = None, offset: int = 0) -> List[Page]:
        """
        List pages from Notion workspace.
        
        This implementation searches for pages in the workspace.
        
        Args:
            limit: Maximum number of pages to return
            offset: Number of pages to skip (not directly supported by Notion)
            
        Returns:
            List of page entities
            
        Raises:
            PageRetrievalError: If listing operation fails
        """
        try:
            # Search for pages using Notion's search API
            search_params = {
                "filter": {
                    "value": "page",
                    "property": "object"
                },
                "sort": {
                    "direction": "descending",
                    "timestamp": "last_edited_time"
                }
            }
            
            if limit:
                search_params["page_size"] = min(limit, 100)  # Notion max is 100
            
            response = await self._run_sync(
                self.client.search,
                **search_params
            )
            
            pages = []
            for page_data in response.get("results", []):
                if page_data.get("object") == "page":
                    # Get full page details including content
                    full_page = await self.get_page_by_id(page_data["id"])
                    if full_page:
                        pages.append(full_page)
            
            # Handle offset by skipping items (simple implementation)
            if offset > 0:
                pages = pages[offset:]
            return pages
          
        except (HTTPResponseError, APIResponseError, RequestTimeoutError) as e:
            raise PageRetrievalError(f"Failed to list pages from Notion: {str(e)}")
            
        except Exception as e:
            raise PageRetrievalError(f"Unexpected error during page listing: {str(e)}")
    
    async def page_exists(self, page_id: str) -> bool:
        """
        Check if a page exists in Notion.
        
        Args:
            page_id: Notion page ID
            
        Returns:
            True if page exists, False otherwise
            
        Raises:
            PageRetrievalError: If existence check fails
        """
        try:
            page = await self.get_page_by_id(page_id)
            return page is not None
        except PageRetrievalError:
            raise
        except Exception as e:
            raise PageRetrievalError(f"Unexpected error during page existence check: {str(e)}")
    
    # Private helper methods
    
    async def _run_sync(self, func, *args, **kwargs):
        """Run synchronous Notion API calls in async context."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    
    def _get_parent_page_id(self) -> str:
        """
        Get the parent page ID for creating new pages.
        
        For this MVP, we'll need to configure a parent page ID.
        In a full implementation, this would be more sophisticated.
        """
        parent_id = self.auth_adapter.get_notion_database_id()
        if not parent_id:
            # For MVP, we'll need to provide a default parent page
            # This should be configured via environment variables
            raise ValidationError(
                "NOTION_DATABASE_ID environment variable is required for creating pages."
            )
        return parent_id
    
    def _build_page_properties(self, page: Page) -> Dict[str, Any]:
        """Build Notion page properties from domain Page entity."""
        properties = {}

        if page.title:
            properties["title"] = {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": page.title}
                    }
                ]
            }

        return properties

    def _build_database_page_properties(self, page: Page) -> Dict[str, Any]:
        """
        Build Notion page properties for a database page.

        Uses page.title for the TITLE property and page.metadata['properties']
        for other database properties.

        Args:
            page: Page entity with metadata['properties'] containing property values

        Returns:
            Dictionary of Notion-formatted properties
        """
        properties = {}

        # Add title property (maps to database's TITLE property)
        if page.title:
            # Find the title property name from the database
            # For now, assume it's named "Name" or the first TITLE property
            # In a real implementation, we'd query the database schema first
            properties["Name"] = {  # This should match the TITLE property name in the database
                "title": [
                    {
                        "type": "text",
                        "text": {"content": page.title}
                    }
                ]
            }

        # Add other properties from metadata
        if page.metadata and "properties" in page.metadata:
            for prop_name, prop_value in page.metadata["properties"].items():
                properties[prop_name] = self._format_property_value(prop_name, prop_value)

        return properties

    def _format_property_value(self, prop_name: str, value: Any) -> Dict[str, Any]:
        """
        Format a property value for Notion API.

        Args:
            prop_name: Property name
            value: Property value (can be string, number, bool, etc.)

        Returns:
            Notion-formatted property value
        """
        # Simple implementation - infer type from value
        if isinstance(value, bool):
            return {"checkbox": value}
        elif isinstance(value, (int, float)):
            return {"number": value}
        elif isinstance(value, str):
            # Could be rich_text, select, url, email, etc.
            # For MVP, treat as select if it looks like a status, otherwise rich_text
            if prop_name in ["Status", "Priority", "Category"]:
                return {"select": {"name": value}}
            else:
                return {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": value}
                        }
                    ]
                }
        elif isinstance(value, list):
            # Multi-select
            return {"multi_select": [{"name": v} for v in value]}
        else:
            # Default to rich_text
            return {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": str(value)}
                    }
                ]
            }

    def _build_page_children(self, page: Page) -> List[Dict[str, Any]]:
        """Build Notion page children blocks from domain Page entity."""
        children = []
        
        if page.content:
            # Simple paragraph block with the content
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": page.content}
                        }
                    ]
                }
            })
        
        return children
    
    def _map_notion_response_to_page(self, notion_response: Dict[str, Any]) -> Page:
        """Map Notion API response to domain Page entity."""
        page_id = notion_response["id"]
        
        # Extract title from properties
        title = ""
        properties = notion_response.get("properties", {})
        title_prop = properties.get("title", {})
        if title_prop and title_prop.get("title"):
            title_parts = title_prop["title"]
            if title_parts:
                title = "".join([part.get("text", {}).get("content", "") for part in title_parts])
        
        # Extract timestamps
        created_time = notion_response.get("created_time")
        last_edited_time = notion_response.get("last_edited_time")
        
        created_at = datetime.fromisoformat(created_time.replace("Z", "+00:00")) if created_time else None
        updated_at = datetime.fromisoformat(last_edited_time.replace("Z", "+00:00")) if last_edited_time else None
        
        return Page(
            id=page_id,
            title=title,
            content="",  # Content will be loaded separately
            created_at=created_at,
            updated_at=updated_at,
            metadata={"notion_url": notion_response.get("url", "")}
        )
    
    def _map_notion_page_to_domain(self, page_response: Dict[str, Any], blocks_response: Dict[str, Any]) -> Page:
        """Map Notion page and blocks to domain Page entity."""
        # Start with basic page info
        page = self._map_notion_response_to_page(page_response)
        
        # Extract content from blocks
        content = ""
        blocks = blocks_response.get("results", [])
        for block in blocks:
            if block.get("type") == "paragraph":
                paragraph = block.get("paragraph", {})
                rich_text = paragraph.get("rich_text", [])
                for text_obj in rich_text:
                    if text_obj.get("type") == "text":
                        content += text_obj.get("text", {}).get("content", "")
                content += "\n"  # Add newline after each paragraph
        
        # Create new page with content
        return Page(
            id=page.id,
            title=page.title,
            content=content.strip(),
            created_at=page.created_at,
            updated_at=page.updated_at,
            metadata=page.metadata
        )
    
    async def _update_page_content(self, page_id: str, content: str):
        """Update page content by replacing all blocks."""
        # Get existing blocks
        blocks_response = await self._run_sync(
            self.client.blocks.children.list,
            block_id=page_id
        )
        
        # Delete existing blocks
        for block in blocks_response.get("results", []):
            await self._run_sync(
                self.client.blocks.delete,
                block_id=block["id"]
            )
        
        # Add new content
        if content.strip():
            children = [{
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": content}
                        }
                    ]
                }
            }]
            
            await self._run_sync(
                self.client.blocks.children.append,
                block_id=page_id,
                children=children
            )

    # Database CRUD Operations

    async def create_database(self, database: Database) -> Database:
        """
        Create a new database in Notion.

        Args:
            database: Database entity to create

        Returns:
            Created database with Notion ID

        Raises:
            DatabaseCreationError: If database creation fails
            ValidationError: If database data is invalid
        """
        from ...domain.exceptions import DatabaseCreationError

        try:
            if database.has_id():
                raise ValidationError("Database already has an ID. Use update_database instead.")

            if not database.is_valid():
                raise ValidationError("Database validation failed")

            # Build database request payload
            payload: Dict[str, Any] = {
                "properties": {}
            }

            # Add title
            payload["title"] = [{"text": {"content": database.title}}]

            # Add description if provided
            if database.description:
                payload["description"] = [{"text": {"content": database.description}}]

            # Add properties schema
            for prop_name, prop in database.properties.items():
                payload["properties"][prop_name] = prop.to_notion_format()

            # Add parent
            if database.parent_id:
                payload["parent"] = {"type": "page_id", "page_id": database.parent_id}
            else:
                payload["parent"] = {"type": "workspace", "workspace": True}

            # Make API call
            response = await self._run_sync(
                self.client.databases.create,
                **payload
            )

            return self._map_notion_database_to_entity(response)

        except (HTTPResponseError, APIResponseError, RequestTimeoutError) as e:
            raise DatabaseCreationError(f"Failed to create database in Notion: {str(e)}")
        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseCreationError(f"Unexpected error during database creation: {str(e)}")

    async def get_database(self, database_id: str) -> Optional[Database]:
        """
        Retrieve a database from Notion by ID.

        Args:
            database_id: Notion database ID

        Returns:
            Database entity if found, None if not found

        Raises:
            DatabaseRetrievalError: If retrieval operation fails
        """
        from ...domain.exceptions import DatabaseRetrievalError

        try:
            response = await self._run_sync(
                self.client.databases.retrieve,
                database_id=database_id
            )

            return self._map_notion_database_to_entity(response)

        except APIResponseError as e:
            if e.status == 404:
                return None
            raise DatabaseRetrievalError(f"Failed to retrieve database from Notion: {str(e)}")
        except (HTTPResponseError, RequestTimeoutError) as e:
            raise DatabaseRetrievalError(f"Failed to retrieve database from Notion: {str(e)}")
        except Exception as e:
            raise DatabaseRetrievalError(f"Unexpected error during database retrieval: {str(e)}")

    async def update_database(self, database: Database) -> Database:
        """
        Update an existing database in Notion.

        Args:
            database: Database entity with updated data (must have ID)

        Returns:
            Updated database entity

        Raises:
            DatabaseNotFoundError: If database does not exist
            DatabaseUpdateError: If update operation fails
            ValidationError: If database data is invalid
        """
        from ...domain.exceptions import DatabaseNotFoundError, DatabaseUpdateError

        try:
            if not database.has_id():
                raise ValidationError("Database must have an ID to be updated.")

            if not database.is_valid():
                raise ValidationError("Database validation failed")

            # Build update payload
            payload: Dict[str, Any] = {}

            # Update title
            payload["title"] = [{"text": {"content": database.title}}]

            # Update description
            if database.description:
                payload["description"] = [{"text": {"content": database.description}}]
            else:
                payload["description"] = []

            # Update properties schema
            payload["properties"] = {}
            for prop_name, prop in database.properties.items():
                payload["properties"][prop_name] = prop.to_notion_format()

            # Make API call
            response = await self._run_sync(
                self.client.databases.update,
                database_id=database.id,
                **payload
            )

            return self._map_notion_database_to_entity(response)

        except APIResponseError as e:
            if e.status == 404:
                raise DatabaseNotFoundError(database.id)
            raise DatabaseUpdateError(f"Failed to update database in Notion: {str(e)}")
        except (HTTPResponseError, RequestTimeoutError) as e:
            raise DatabaseUpdateError(f"Failed to update database in Notion: {str(e)}")
        except (DatabaseNotFoundError, ValidationError):
            raise
        except Exception as e:
            raise DatabaseUpdateError(f"Unexpected error during database update: {str(e)}")

    async def delete_database(self, database_id: str, confirm: bool = False) -> bool:
        """
        Delete (archive) a database in Notion.

        Args:
            database_id: Notion database ID
            confirm: Confirmation flag for destructive operation (required)

        Returns:
            True if database was archived, False if not found or not confirmed

        Raises:
            DatabaseDeletionError: If deletion operation fails
        """
        from ...domain.exceptions import DatabaseDeletionError

        try:
            # Require explicit confirmation for safety
            if not confirm:
                return False

            # Archive the database
            await self._run_sync(
                self.client.databases.update,
                database_id=database_id,
                archived=True
            )
            return True

        except APIResponseError as e:
            if e.status == 404:
                return False
            raise DatabaseDeletionError(f"Failed to delete database in Notion: {str(e)}")
        except (HTTPResponseError, RequestTimeoutError) as e:
            raise DatabaseDeletionError(f"Failed to delete database in Notion: {str(e)}")
        except Exception as e:
            raise DatabaseDeletionError(f"Unexpected error during database deletion: {str(e)}")

    async def query_database_pages(self, database_id: str) -> List[Page]:
        """
        Query pages in a database.

        Args:
            database_id: Notion database ID

        Returns:
            List of Page entities in the database

        Raises:
            PageRetrievalError: If query operation fails
        """
        try:
            response = await self._run_sync(
                self.client.databases.query,
                database_id=database_id
            )

            pages = []
            for page_data in response.get("results", []):
                # Get full page details
                full_page = await self.get_page_by_id(page_data["id"])
                if full_page:
                    pages.append(full_page)

            return pages

        except (HTTPResponseError, APIResponseError, RequestTimeoutError) as e:
            raise PageRetrievalError(f"Failed to query database pages: {str(e)}")
        except Exception as e:
            raise PageRetrievalError(f"Unexpected error during database query: {str(e)}")

    def _map_notion_database_to_entity(self, notion_response: Dict[str, Any]) -> Database:
        """
        Map Notion API database response to Database entity.

        Args:
            notion_response: Notion API response for a database

        Returns:
            Database entity
        """
        # Extract ID
        database_id = notion_response["id"]

        # Extract title
        title = ""
        title_array = notion_response.get("title", [])
        if title_array:
            title = "".join([item.get("text", {}).get("content", "") for item in title_array])

        # Extract description
        description = None
        desc_array = notion_response.get("description", [])
        if desc_array:
            description = "".join([item.get("text", {}).get("content", "") for item in desc_array])

        # Extract properties
        properties: Dict[str, DatabaseProperty] = {}
        props_data = notion_response.get("properties", {})

        for prop_name, prop_data in props_data.items():
            prop_type_str = prop_data.get("type", "")

            # Map Notion type to PropertyType enum
            prop_type = self._map_notion_type_to_enum(prop_type_str)

            # Extract configuration
            config: Dict[str, Any] = {}
            if prop_type == PropertyType.SELECT and "select" in prop_data:
                config["options"] = prop_data["select"].get("options", [])
            elif prop_type == PropertyType.MULTI_SELECT and "multi_select" in prop_data:
                config["options"] = prop_data["multi_select"].get("options", [])
            elif prop_type == PropertyType.NUMBER and "number" in prop_data:
                if "format" in prop_data["number"]:
                    config["format"] = prop_data["number"]["format"]

            properties[prop_name] = DatabaseProperty(
                name=prop_name,
                property_type=prop_type,
                config=config
            )

        # Extract timestamps
        created_time = notion_response.get("created_time")
        last_edited_time = notion_response.get("last_edited_time")

        created_at = datetime.fromisoformat(created_time.replace("Z", "+00:00")) if created_time else None
        updated_at = datetime.fromisoformat(last_edited_time.replace("Z", "+00:00")) if last_edited_time else None

        # Extract metadata
        metadata = {
            "notion_url": notion_response.get("url", ""),
            "archived": notion_response.get("archived", False)
        }

        return Database(
            id=database_id,
            title=title,
            description=description,
            properties=properties,
            parent_id=None,  # Parent info not returned in retrieve
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata
        )

    def _map_notion_type_to_enum(self, notion_type: str) -> PropertyType:
        """
        Map Notion property type string to PropertyType enum.

        Args:
            notion_type: Notion API property type string

        Returns:
            PropertyType enum value
        """
        type_mapping = {
            "title": PropertyType.TITLE,
            "rich_text": PropertyType.RICH_TEXT,
            "number": PropertyType.NUMBER,
            "select": PropertyType.SELECT,
            "multi_select": PropertyType.MULTI_SELECT,
            "date": PropertyType.DATE,
            "checkbox": PropertyType.CHECKBOX,
            "url": PropertyType.URL,
            "email": PropertyType.EMAIL
        }

        return type_mapping.get(notion_type, PropertyType.RICH_TEXT)