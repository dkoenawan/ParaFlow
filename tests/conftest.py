"""
Pytest Configuration

Global pytest configuration and fixtures for the entire test suite.
Provides common test setup, fixtures, and configuration for all tests.
"""

import pytest
from typing import Generator


@pytest.fixture
def sample_fixture() -> str:
    """
    Sample fixture for demonstration purposes.
    Replace with actual project-specific fixtures.
    """
    return "sample_data"


# Add pytest configuration options here
def pytest_configure(config):
    """Configure pytest with custom markers and options."""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


# Add custom pytest collection rules if needed
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on path."""
    for item in items:
        # Add markers based on test file path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)