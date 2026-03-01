from __future__ import annotations

import pytest

from noteshift.notion import NotionClient


@pytest.mark.contract
@pytest.mark.vcr(cassette_library_dir="tests/contract/cassettes")
def test_get_page_contract_replay() -> None:
    """Replay a deterministic Notion get page API interaction from cassette."""
    client = NotionClient(token="secret_dummy")

    payload = client.get_page("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")

    assert payload["id"] == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    assert payload["object"] == "page"
