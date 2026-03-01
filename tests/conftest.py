from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_notion_client() -> MagicMock:
    """Provide a mock Notion client instance for unit tests."""
    return MagicMock()


@pytest.fixture(scope="module")
def vcr_config() -> dict[str, object]:
    """Configure pytest-vcr to scrub secret headers from cassettes."""
    return {
        "filter_headers": [("authorization", "DUMMY")],
        "filter_query_parameters": [("token", "DUMMY")],
        "record_mode": "none",
    }
