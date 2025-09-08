"""
Authentication adapter for external services.

This module provides authentication functionality for connecting to
external services like Notion. It handles environment variable loading
and secure credential management.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class AuthenticationAdapter:
    """
    Handles authentication credentials and configuration.
    
    This adapter manages secure credential loading from environment
    variables and provides authentication tokens for external services.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the authentication adapter.
        
        Args:
            env_file: Path to .env file. If None, uses default .env lookup
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
    
    def get_notion_token(self) -> str:
        """
        Get the Notion integration token from environment variables.
        
        Returns:
            Notion integration token
            
        Raises:
            ValueError: If token is not found or empty
        """
        token = os.getenv('NOTION_TOKEN')
        if not token or not token.strip():
            raise ValueError(
                "NOTION_TOKEN environment variable is required. "
                "Please set it to your Notion integration token."
            )
        return token.strip()
    
    def get_notion_database_id(self) -> Optional[str]:
        """
        Get the Notion database ID from environment variables.
        
        Returns:
            Notion database ID if configured, None otherwise
        """
        database_id = os.getenv('NOTION_DATABASE_ID')
        return database_id.strip() if database_id else None
    
    def validate_configuration(self) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If required configuration is missing
        """
        try:
            self.get_notion_token()
            return True
        except ValueError as e:
            raise ValueError(f"Configuration validation failed: {e}")