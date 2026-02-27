from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_notion_client():
    """Provides a mock NotionClient instance."""
    client = MagicMock()
    # You can configure mock client methods and return values here
    # Example:
    # client.pages.list.return_value = [
    #     {"id": "123", "properties": {"Name": {"title": [{"text": {"content": "Test Page"}}]}}}
    # ]
    return client

# Add other fixtures as needed, e.g., for specific page data, database structures, etc.
