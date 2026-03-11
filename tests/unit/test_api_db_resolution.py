from __future__ import annotations

from pathlib import Path

import pytest

from noteshift.api import run_export
from noteshift.types import ExportPlan, NoteshiftConfig


def test_run_export_database_id_is_resolved(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """run_export should accept database_id inputs and resolve to data_source_id."""

    # Stub NotionClient used inside noteshift.api
    class _Client:
        def __init__(self, token: str):
            self.token = token

        def resolve_data_source_id(self, raw: str) -> str:
            assert raw == "db-raw"
            return "ds-1"

        def get_data_source(self, data_source_id: str) -> dict:
            assert data_source_id == "ds-1"
            # Minimal schema payload for title extraction.
            return {"title": [{"plain_text": "My DB"}]}

    monkeypatch.setattr("noteshift.api.NotionClient", _Client)

    called: dict[str, str] = {}

    def fake_export_child_database(*, client, data_source_id: str, title: str, out_dir):
        _ = client
        _ = out_dir
        called["data_source_id"] = data_source_id
        called["title"] = title

        class _Res:
            warnings: list[str] = []
            files_written: int = 0
            data_sources_exported: int = 1
            rows_exported: int = 0
            attachments_downloaded: int = 0

        return _Res()

    monkeypatch.setattr(
        "noteshift.api.export_child_database", fake_export_child_database
    )

    config = NoteshiftConfig(notion_token="t", out_dir=tmp_path / "out", overwrite=True)
    plan = ExportPlan(page_ids=[], database_ids=["db-raw"])

    res = run_export(plan, config)

    assert res.databases_exported == 1
    assert called["data_source_id"] == "ds-1"
    assert called["title"] == "My DB"
