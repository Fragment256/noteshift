from __future__ import annotations

from pathlib import Path

import pytest

from noteshift.notion import NotionClient


class _FakeResponse:
    def __init__(self, payload: dict, *, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.content = b"file-bytes"

    def raise_for_status(self) -> None:
        # Tests use this as a no-op; callers may branch on status_code directly.
        return None

    def json(self) -> dict:
        return self._payload


class _FakeClient:
    def __init__(self, responses: list[_FakeResponse]) -> None:
        self._responses = responses

    def __enter__(self) -> _FakeClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def get(self, _url: str, params=None):
        _ = params
        return self._responses.pop(0)

    def post(self, _url: str, json=None):
        _ = json
        return self._responses.pop(0)


def test_list_block_children_handles_pagination(monkeypatch) -> None:
    responses = [
        _FakeResponse(
            {"results": [{"id": "a"}], "has_more": True, "next_cursor": "c1"}
        ),
        _FakeResponse(
            {"results": [{"id": "b"}], "has_more": False, "next_cursor": None}
        ),
    ]

    monkeypatch.setattr(
        "noteshift.notion.httpx.Client", lambda **_kwargs: _FakeClient(responses)
    )

    client = NotionClient(token="secret")
    blocks = client.list_block_children("block-1")

    assert [block["id"] for block in blocks] == ["a", "b"]


def test_query_data_source_handles_pagination(monkeypatch) -> None:
    responses = [
        _FakeResponse(
            {"results": [{"id": "r1"}], "has_more": True, "next_cursor": "c1"}
        ),
        _FakeResponse(
            {"results": [{"id": "r2"}], "has_more": False, "next_cursor": None}
        ),
    ]

    monkeypatch.setattr(
        "noteshift.notion.httpx.Client", lambda **_kwargs: _FakeClient(responses)
    )

    client = NotionClient(token="secret")
    rows = client.query_data_source("db-1")

    assert [row["id"] for row in rows] == ["r1", "r2"]


def test_download_file_writes_content(monkeypatch, tmp_path: Path) -> None:
    responses = [_FakeResponse({})]
    monkeypatch.setattr(
        "noteshift.notion.httpx.Client", lambda **_kwargs: _FakeClient(responses)
    )

    client = NotionClient(token="secret")
    dest = tmp_path / "asset.bin"
    client.download_file("https://example.com/file.bin", dest)

    assert dest.exists()
    assert dest.read_bytes() == b"file-bytes"


def test_resolve_data_source_id_accepts_data_source_id(monkeypatch) -> None:
    responses = [
        _FakeResponse({"object": "data_source", "id": "ds-1"}, status_code=200),
    ]

    monkeypatch.setattr(
        "noteshift.notion.httpx.Client", lambda **_kwargs: _FakeClient(responses)
    )

    client = NotionClient(token="secret")
    assert client.resolve_data_source_id("ds-1") == "ds-1"


def test_resolve_data_source_id_falls_back_from_database_id(monkeypatch) -> None:
    responses = [
        _FakeResponse({"object": "error"}, status_code=404),
        _FakeResponse(
            {"object": "database", "data_sources": [{"id": "ds-2"}]},
            status_code=200,
        ),
    ]

    monkeypatch.setattr(
        "noteshift.notion.httpx.Client", lambda **_kwargs: _FakeClient(responses)
    )

    client = NotionClient(token="secret")
    assert client.resolve_data_source_id("db-1") == "ds-2"


def test_resolve_data_source_id_raises_no_data_sources(monkeypatch) -> None:
    responses = [
        _FakeResponse({"object": "error"}, status_code=404),
        _FakeResponse({"object": "database", "data_sources": []}, status_code=200),
    ]

    monkeypatch.setattr(
        "noteshift.notion.httpx.Client", lambda **_kwargs: _FakeClient(responses)
    )

    client = NotionClient(token="secret")

    with pytest.raises(RuntimeError):
        client.resolve_data_source_id("db-1")
