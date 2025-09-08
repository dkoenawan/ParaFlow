#!/usr/bin/env python3
"""
Demo script for Notion API MVP.

This script demonstrates the basic CRUD operations available in the
Notion API MVP implementation. It shows how to:
1. Set up authentication and configuration
2. Create a new page
3. Read the created page
4. Update the page content
5. Delete the page

Before running this script, make sure to:
1. Set up your .env file with NOTION_TOKEN and NOTION_DATABASE_ID
2. Install dependencies: pip install notion-client python-dotenv

Usage:
    python examples/demo_script.py
"""

import asyncio
import sys
from pathlib import Path

# Add the packages directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.infrastructure.adapters.auth import AuthenticationAdapter
from packages.infrastructure.adapters.notion_adapter import NotionPageRepositoryAdapter
from packages.application.use_cases.page_operations import PageApplicationService


async def main():
    """Main demo function demonstrating CRUD operations."""
    print("🚀 Notion API MVP Demo")
    print("=" * 50)
    
    try:
        # 1. Set up authentication and services
        print("\n1. Setting up authentication...")
        auth_adapter = AuthenticationAdapter()
        auth_adapter.validate_configuration()
        print("✅ Authentication configured successfully")
        
        notion_adapter = NotionPageRepositoryAdapter(auth_adapter)
        app_service = PageApplicationService(notion_adapter)
        print("✅ Services initialized")
        
        # 2. Create a new page
        print("\n2. Creating a new page...")
        page_title = "Demo Page - PARA Framework MVP"
        page_content = """This is a demo page created by the PARA Framework Notion API MVP.

Features demonstrated:
- ✅ Page creation with title and content
- ✅ Proper authentication handling
- ✅ Clean architecture with ports and adapters
- ✅ Domain-driven design principles

This page will be updated and then deleted as part of the demo."""
        
        created_page = await app_service.create_page(
            title=page_title,
            content=page_content,
            metadata={"demo": True, "framework": "PARA"}
        )
        
        print(f"✅ Page created successfully!")
        print(f"   ID: {created_page.id}")
        print(f"   Title: {created_page.title}")
        print(f"   Content length: {len(created_page.content)} characters")
        print(f"   Created at: {created_page.created_at}")
        
        # 3. Read the created page
        print("\n3. Reading the created page...")
        retrieved_page = await app_service.get_page(created_page.id)
        
        print(f"✅ Page retrieved successfully!")
        print(f"   Title: {retrieved_page.title}")
        print(f"   Updated at: {retrieved_page.updated_at}")
        print(f"   Has content: {'Yes' if retrieved_page.content else 'No'}")
        
        # 4. Update the page
        print("\n4. Updating the page...")
        updated_title = f"{page_title} - Updated"
        updated_content = f"{page_content}\n\n--- UPDATE ---\nThis content was added during the demo update operation."
        
        updated_page = await app_service.update_page(
            page_id=created_page.id,
            title=updated_title,
            content=updated_content
        )
        
        print(f"✅ Page updated successfully!")
        print(f"   New title: {updated_page.title}")
        print(f"   New content length: {len(updated_page.content)} characters")
        
        # 5. List pages (show first few)
        print("\n5. Listing pages in workspace...")
        pages = await app_service.list_pages(limit=5)
        print(f"✅ Found {len(pages)} pages (showing up to 5):")
        for i, page in enumerate(pages, 1):
            print(f"   {i}. {page.title[:50]}..." if len(page.title) > 50 else f"   {i}. {page.title}")
        
        # 6. Check page existence
        print("\n6. Checking page existence...")
        exists = await app_service.page_exists(created_page.id)
        print(f"✅ Page exists: {exists}")
        
        # 7. Delete the page
        print("\n7. Cleaning up - deleting the demo page...")
        deleted = await app_service.delete_page(created_page.id)
        
        if deleted:
            print("✅ Page deleted successfully!")
            
            # Verify deletion
            exists_after_delete = await app_service.page_exists(created_page.id)
            print(f"   Page exists after deletion: {exists_after_delete}")
        else:
            print("❌ Page deletion failed or page did not exist")
        
        print("\n🎉 Demo completed successfully!")
        print("\nThe Notion API MVP is working correctly with the following features:")
        print("  ✅ Create pages with title and content")
        print("  ✅ Read pages by ID")
        print("  ✅ Update existing pages")
        print("  ✅ Delete pages")
        print("  ✅ List pages with pagination")
        print("  ✅ Check page existence")
        print("  ✅ Proper error handling and validation")
        print("  ✅ Clean hexagonal architecture implementation")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Provide helpful troubleshooting tips
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure your .env file is configured with:")
        print("   - NOTION_TOKEN: Your Notion integration token")
        print("   - NOTION_DATABASE_ID: ID of a page in your workspace")
        print("2. Ensure your Notion integration has the required permissions")
        print("3. Check that the database/page ID is valid and accessible")
        print("4. Verify your internet connection")
        
        return 1
    
    return 0


def print_configuration_help():
    """Print help for setting up the configuration."""
    print("\n📋 Configuration Setup Help")
    print("=" * 50)
    print("\nTo run this demo, you need to:")
    print("\n1. Create a Notion Integration:")
    print("   - Go to https://www.notion.so/my-integrations")
    print("   - Click 'New integration'")
    print("   - Give it a name and select your workspace")
    print("   - Copy the 'Internal Integration Token'")
    print("\n2. Share a page with your integration:")
    print("   - Open a page in Notion")
    print("   - Click 'Share' in the top right")
    print("   - Invite your integration")
    print("   - Copy the page ID from the URL")
    print("\n3. Create a .env file in the project root:")
    print("   NOTION_TOKEN=your_integration_token_here")
    print("   NOTION_DATABASE_ID=your_page_id_here")
    print("\n4. Install dependencies:")
    print("   pip install notion-client python-dotenv")


if __name__ == "__main__":
    try:
        # Check if configuration exists
        auth = AuthenticationAdapter()
        auth.validate_configuration()
        
        # Run the demo
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
    except ValueError as e:
        print("❌ Configuration Error:")
        print(f"   {e}")
        print_configuration_help()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)