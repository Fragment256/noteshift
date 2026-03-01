from __future__ import annotations

import pytest

from noteshift.notion import NotionClient


@pytest.mark.contract
@pytest.mark.vcr(cassette_library_dir="tests/contract/cassettes")
def test_query_data_source_contract_replay() -> None:
    """Replay deterministic query interaction from cassette."""
    client = NotionClient(token="secret_dummy")

    rows = client.query_data_source("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")

    assert len(rows) == 2
    assert rows[0]["id"] == "row-1"
