"""
Integration tests for Notion API MVP.

This module contains integration tests that verify the entire CRUD workflow
works correctly with the actual Notion API. These tests require proper
environment configuration and a test Notion workspace.

To run these tests, set the following environment variables:
- NOTION_TOKEN: Your Notion integration token
- NOTION_DATABASE_ID: ID of a test page/database in your workspace

NOTE: These tests will create, modify, and delete actual pages in your Notion workspace.
Use a dedicated test workspace to avoid affecting production data.
"""

import pytest
import os
import asyncio
from datetime import datetime

from packages.domain.models.page import Page
from packages.domain.exceptions import PageNotFoundError, ValidationError
from packages.infrastructure.adapters.auth import AuthenticationAdapter
from packages.infrastructure.adapters.notion_adapter import NotionPageRepositoryAdapter
from packages.application.use_cases.page_operations import PageApplicationService


# Skip integration tests if environment is not configured
pytestmark = pytest.mark.skipif(
    not os.getenv('NOTION_TOKEN') or not os.getenv('NOTION_DATABASE_ID'),
    reason="Integration tests require NOTION_TOKEN and NOTION_DATABASE_ID environment variables"
)


class TestNotionIntegration:
    """
    Integration tests for Notion API operations.
    
    These tests verify that the complete system works correctly with the
    actual Notion API, from domain models through adapters to external service.
    """
    
    @pytest.fixture(scope="class")
    def auth_adapter(self):
        """Authentication adapter for integration tests."""
        return AuthenticationAdapter()
    
    @pytest.fixture(scope="class")
    def notion_adapter(self, auth_adapter):
        """Notion adapter for integration tests."""
        return NotionPageRepositoryAdapter(auth_adapter)
    
    @pytest.fixture(scope="class")
    def app_service(self, notion_adapter):
        """Application service for integration tests."""
        return PageApplicationService(notion_adapter)
    
    @pytest.fixture
    def test_page_data(self):
        """Test data for creating pages."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return {
            "title": f"Test Page {timestamp}",
            "content": f"This is test content created at {timestamp} for integration testing.",
            "metadata": {"test": True, "created_by": "integration_test"}
        }
    
    @pytest.mark.asyncio
    async def test_authentication_validation(self, auth_adapter):
        """Test that authentication configuration is valid."""
        # This should not raise an exception if properly configured
        auth_adapter.validate_configuration()
        
        # Verify we can get required configuration
        token = auth_adapter.get_notion_token()
        assert token is not None and token.strip() != ""
        
        database_id = auth_adapter.get_notion_database_id()
        assert database_id is not None and database_id.strip() != ""
    
    @pytest.mark.asyncio
    async def test_create_page_full_workflow(self, app_service, test_page_data):
        """Test creating a page through the full application stack."""
        # Create page
        created_page = await app_service.create_page(
            title=test_page_data["title"],
            content=test_page_data["content"],
            metadata=test_page_data["metadata"]
        )
        
        # Verify page was created
        assert created_page is not None
        assert created_page.has_id()
        assert created_page.title == test_page_data["title"]
        assert created_page.content == test_page_data["content"]
        assert created_page.created_at is not None
        assert created_page.updated_at is not None
        
        # Clean up - delete the created page
        deleted = await app_service.delete_page(created_page.id)
        assert deleted is True
    
    @pytest.mark.asyncio
    async def test_crud_operations_workflow(self, app_service, test_page_data):
        """Test complete CRUD workflow: Create -> Read -> Update -> Delete."""
        created_page = None
        
        try:
            # CREATE
            created_page = await app_service.create_page(
                title=test_page_data["title"],
                content=test_page_data["content"]
            )
            
            assert created_page.has_id()
            original_id = created_page.id
            
            # READ
            retrieved_page = await app_service.get_page(original_id)
            assert retrieved_page.id == original_id
            assert retrieved_page.title == test_page_data["title"]
            # Note: Content might have minor formatting differences from Notion
            
            # UPDATE
            updated_title = f"{test_page_data['title']} - Updated"
            updated_content = f"{test_page_data['content']} - Updated content"
            
            updated_page = await app_service.update_page(
                page_id=original_id,
                title=updated_title,
                content=updated_content
            )
            
            assert updated_page.id == original_id
            assert updated_page.title == updated_title
            # Note: Content updates might take time to reflect in Notion
            
            # Verify update by reading again
            final_page = await app_service.get_page(original_id)
            assert final_page.title == updated_title
            
            # DELETE
            deleted = await app_service.delete_page(original_id)
            assert deleted is True
            
            # Verify deletion
            with pytest.raises(PageNotFoundError):
                await app_service.get_page(original_id)
        
        finally:
            # Cleanup in case test fails
            if created_page and created_page.has_id():
                try:
                    await app_service.delete_page(created_page.id)
                except:
                    pass  # Ignore cleanup errors
    
    @pytest.mark.asyncio
    async def test_page_exists_functionality(self, app_service, test_page_data):
        """Test page existence checking functionality."""
        created_page = None
        
        try:
            # Create a page
            created_page = await app_service.create_page(
                title=test_page_data["title"],
                content=test_page_data["content"]
            )
            
            # Test exists returns True for existing page
            exists = await app_service.page_exists(created_page.id)
            assert exists is True
            
            # Delete the page
            deleted = await app_service.delete_page(created_page.id)
            assert deleted is True
            
            # Test exists returns False for deleted page
            exists = await app_service.page_exists(created_page.id)
            assert exists is False
            
            created_page = None  # Mark as cleaned up
            
        finally:
            # Cleanup
            if created_page and created_page.has_id():
                try:
                    await app_service.delete_page(created_page.id)
                except:
                    pass
    
    @pytest.mark.asyncio
    async def test_list_pages_functionality(self, app_service, test_page_data):
        """Test listing pages functionality."""
        created_pages = []
        
        try:
            # Create multiple test pages
            for i in range(3):
                page_data = test_page_data.copy()
                page_data["title"] = f"{test_page_data['title']} - {i}"
                
                created_page = await app_service.create_page(
                    title=page_data["title"],
                    content=page_data["content"]
                )
                created_pages.append(created_page)
            
            # List pages (may include other pages in workspace)
            pages = await app_service.list_pages(limit=10)
            
            # Verify our created pages are in the list
            created_ids = {page.id for page in created_pages}
            retrieved_ids = {page.id for page in pages}
            
            assert created_ids.issubset(retrieved_ids), "Created pages should be found in list"
            
        finally:
            # Cleanup all created pages
            for page in created_pages:
                try:
                    await app_service.delete_page(page.id)
                except:
                    pass  # Ignore cleanup errors
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_page_id(self, app_service):
        """Test error handling for invalid page IDs."""
        # Test with non-existent page ID
        with pytest.raises(PageNotFoundError):
            await app_service.get_page("non-existent-id-12345")
        
        # Test page existence for non-existent page
        exists = await app_service.page_exists("non-existent-id-12345")
        assert exists is False
        
        # Test deletion of non-existent page
        deleted = await app_service.delete_page("non-existent-id-12345")
        assert deleted is False
    
    @pytest.mark.asyncio
    async def test_validation_errors(self, app_service):
        """Test that validation errors are properly handled."""
        # Test empty title
        with pytest.raises(ValidationError, match="Page title cannot be empty"):
            await app_service.create_page("")
        
        # Test empty page ID
        with pytest.raises(ValidationError, match="Page ID cannot be empty"):
            await app_service.get_page("")


@pytest.fixture
def env_file_path():
    """Path to .env file for testing (optional)."""
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    return env_path if os.path.exists(env_path) else None


class TestEnvironmentConfiguration:
    """Tests for environment configuration and authentication setup."""
    
    def test_auth_adapter_loads_environment_variables(self):
        """Test that AuthenticationAdapter properly loads environment variables."""
        auth = AuthenticationAdapter()
        
        # These will raise ValueError if not configured
        token = auth.get_notion_token()
        database_id = auth.get_notion_database_id()
        
        assert isinstance(token, str) and len(token) > 0
        assert isinstance(database_id, str) and len(database_id) > 0
    
    def test_auth_adapter_validation(self):
        """Test authentication configuration validation."""
        auth = AuthenticationAdapter()
        
        # Should not raise exception if properly configured
        result = auth.validate_configuration()
        assert result is True


# Performance test (optional, can be skipped for regular runs)
@pytest.mark.slow
@pytest.mark.asyncio
async def test_performance_multiple_operations(app_service, test_page_data):
    """
    Performance test for multiple concurrent operations.
    
    This test is marked as 'slow' and can be skipped for regular test runs.
    Run with: pytest -m slow
    """
    created_pages = []
    
    try:
        # Create multiple pages concurrently
        tasks = []
        for i in range(5):
            page_data = test_page_data.copy()
            page_data["title"] = f"{test_page_data['title']} - Perf Test {i}"
            
            task = app_service.create_page(
                title=page_data["title"],
                content=page_data["content"]
            )
            tasks.append(task)
        
        # Wait for all creations to complete
        pages = await asyncio.gather(*tasks)
        created_pages.extend(pages)
        
        # Verify all pages were created
        assert len(pages) == 5
        for page in pages:
            assert page.has_id()
        
        # Read all pages concurrently
        read_tasks = [app_service.get_page(page.id) for page in pages]
        read_pages = await asyncio.gather(*read_tasks)
        
        # Verify all reads succeeded
        assert len(read_pages) == 5
        for page in read_pages:
            assert page.has_id()
        
    finally:
        # Cleanup all created pages
        if created_pages:
            cleanup_tasks = [app_service.delete_page(page.id) for page in created_pages]
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)