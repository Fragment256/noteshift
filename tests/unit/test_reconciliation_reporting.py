from __future__ import annotations

import json
from pathlib import Path

import pytest

from noteshift.api import run_export
from noteshift.types import ExportPlan, NoteshiftConfig


def _load_recon(out_dir: Path) -> dict:
    p = out_dir / "reconciliation_report.json"
    assert p.exists()
    return json.loads(p.read_text(encoding="utf-8"))


def test_reconciliation_records_skipped_and_success(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[str] = []

    def fake_export_page_tree(**kwargs):
        calls.append(kwargs["root_page_id"])
        # Simulate that the exporter updates checkpoint
        kwargs["checkpoint"].add_page(kwargs["root_page_id"])
        kwargs["checkpoint"].add_file("x/index.md")

    monkeypatch.setattr("noteshift.api.export_page_tree", fake_export_page_tree)

    # Create a checkpoint on disk containing p1 already exported
    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True)
    (out_dir / ".checkpoint.json").write_text(
        json.dumps(
            {
                "version": 1,
                "timestamp": "2026-01-01T00:00:00Z",
                "page_ids": ["p1"],
                "database_ids": [],
                "files_written": [],
                "attachments_downloaded": 0,
                "rows_exported": 0,
                "warnings": [],
            }
        ),
        encoding="utf-8",
    )

    config = NoteshiftConfig(notion_token="t", out_dir=out_dir, overwrite=True)
    plan = ExportPlan(page_ids=["p1", "p2"], database_ids=[])

    res = run_export(plan, config)
    assert res.pages_exported == 2  # p1 from checkpoint + p2 newly exported
    assert calls == ["p2"]  # p1 was skipped

    recon = _load_recon(out_dir)
    items = recon["items"]

    assert any(i["id"] == "p1" and i["status"] == "skipped" for i in items)
    assert any(i["id"] == "p2" and i["status"] == "success" for i in items)


def test_reconciliation_db_skip_uses_resolved_id(monkeypatch, tmp_path: Path) -> None:
    # checkpoint stores resolved data_source_id
    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True)
    (out_dir / ".checkpoint.json").write_text(
        json.dumps(
            {
                "version": 1,
                "timestamp": "2026-01-01T00:00:00Z",
                "page_ids": [],
                "database_ids": ["ds-1"],
                "files_written": [],
                "attachments_downloaded": 0,
                "rows_exported": 0,
                "warnings": [],
            }
        ),
        encoding="utf-8",
    )

    class _Client:
        def __init__(self, token: str):
            self.token = token

        def resolve_data_source_id(self, raw: str) -> str:
            assert raw == "db-raw"
            return "ds-1"

        def get_data_source(self, _data_source_id: str) -> dict:  # pragma: no cover
            raise AssertionError("should not query data source when skipped")

    monkeypatch.setattr("noteshift.api.NotionClient", _Client)

    def fake_export_child_database(*_args, **_kwargs):  # pragma: no cover
        raise AssertionError("should not export database when skipped")

    monkeypatch.setattr(
        "noteshift.api.export_child_database", fake_export_child_database
    )

    config = NoteshiftConfig(notion_token="t", out_dir=out_dir, overwrite=True)
    plan = ExportPlan(page_ids=[], database_ids=["db-raw"])

    res = run_export(plan, config)
    assert res.databases_exported == 1

    recon = _load_recon(out_dir)
    assert any(i["id"] == "ds-1" and i["status"] == "skipped" for i in recon["items"])


def test_fail_fast_writes_reconciliation_before_raise(
    monkeypatch, tmp_path: Path
) -> None:
    def boom_export_page_tree(**_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("noteshift.api.export_page_tree", boom_export_page_tree)

    out_dir = tmp_path / "out"
    config = NoteshiftConfig(
        notion_token="t",
        out_dir=out_dir,
        overwrite=True,
        fail_fast=True,
    )
    plan = ExportPlan(page_ids=["p1"], database_ids=[])

    with pytest.raises(RuntimeError):
        run_export(plan, config)

    recon = _load_recon(out_dir)
    assert any(i["id"] == "p1" and i["status"] == "failed" for i in recon["items"])
    assert recon["errors"]


def test_reconciliation_db_success_records_warnings(
    monkeypatch, tmp_path: Path
) -> None:
    out_dir = tmp_path / "out"

    class _Client:
        def __init__(self, token: str):
            self.token = token

        def resolve_data_source_id(self, raw: str) -> str:
            assert raw == "db-raw"
            return "ds-1"

        def get_data_source(self, data_source_id: str) -> dict:
            assert data_source_id == "ds-1"
            return {"title": [{"plain_text": "My DB"}]}

    class _DBResult:
        data_sources_exported = 1
        rows_exported = 3
        files_written = 2
        attachments_downloaded = 0
        warnings = ["w1"]

    def fake_export_child_database(*, client, data_source_id, title, out_dir):
        assert data_source_id == "ds-1"
        assert title == "My DB"
        return _DBResult()

    monkeypatch.setattr("noteshift.api.NotionClient", _Client)
    monkeypatch.setattr(
        "noteshift.api.export_child_database", fake_export_child_database
    )

    config = NoteshiftConfig(notion_token="t", out_dir=out_dir, overwrite=True)
    plan = ExportPlan(page_ids=[], database_ids=["db-raw"])

    res = run_export(plan, config)
    assert res.databases_exported == 1
    assert res.rows_exported == 3
    assert res.warnings == ["w1"]

    recon = _load_recon(out_dir)
    assert recon["warnings"] == ["w1"]
    assert any(i["id"] == "ds-1" and i["status"] == "success" for i in recon["items"])


def test_fail_fast_db_error_writes_reconciliation(monkeypatch, tmp_path: Path) -> None:
    out_dir = tmp_path / "out"

    class _Client:
        def __init__(self, token: str):
            self.token = token

        def resolve_data_source_id(self, raw: str) -> str:
            return "ds-1"

        def get_data_source(self, data_source_id: str) -> dict:
            return {"title": [{"plain_text": "My DB"}]}

    def fake_export_child_database(*_args, **_kwargs):
        raise RuntimeError("db boom")

    monkeypatch.setattr("noteshift.api.NotionClient", _Client)
    monkeypatch.setattr(
        "noteshift.api.export_child_database", fake_export_child_database
    )

    config = NoteshiftConfig(
        notion_token="t",
        out_dir=out_dir,
        overwrite=True,
        fail_fast=True,
    )
    plan = ExportPlan(page_ids=[], database_ids=["db-raw"])

    with pytest.raises(RuntimeError):
        run_export(plan, config)

    recon = _load_recon(out_dir)
    assert any(i["id"] == "db-raw" and i["status"] == "failed" for i in recon["items"])
    assert recon["errors"]


def test_reconciliation_db_includes_summary_fields(
    monkeypatch, tmp_path: Path
) -> None:
    """Test that db reconciliation items include summary fields."""
    out_dir = tmp_path / "out"

    class _Client:
        def __init__(self, token: str):
            self.token = token

        def resolve_data_source_id(self, raw: str) -> str:
            return "ds-1"

        def get_data_source(self, data_source_id: str) -> dict:
            return {"title": [{"plain_text": "My DB"}]}

    class _DBResult:
        data_sources_exported = 1
        rows_exported = 42
        files_written = 3
        attachments_downloaded = 0
        warnings = []

    def fake_export_child_database(*, client, data_source_id, title, out_dir):
        return _DBResult()

    monkeypatch.setattr("noteshift.api.NotionClient", _Client)
    monkeypatch.setattr(
        "noteshift.api.export_child_database", fake_export_child_database
    )

    config = NoteshiftConfig(notion_token="t", out_dir=out_dir, overwrite=True)
    plan = ExportPlan(page_ids=[], database_ids=["db-raw"])

    res = run_export(plan, config)
    assert res.databases_exported == 1
    assert res.rows_exported == 42

    recon = _load_recon(out_dir)
    db_items = [i for i in recon["items"] if i["id"] == "ds-1"]
    assert len(db_items) == 1

    db_item = db_items[0]
    assert db_item["status"] == "success"
    assert db_item["type"] == "database"
    assert db_item["title"] == "My DB"
    assert db_item["rows_exported"] == 42
    assert db_item["files_written"] == 3


def test_reconciliation_db_zero_values_included(monkeypatch, tmp_path: Path) -> None:
    """Test db reconciliation with zero rows/files includes fields."""
    out_dir = tmp_path / "out"

    class _Client:
        def __init__(self, token: str):
            self.token = token

        def resolve_data_source_id(self, raw: str) -> str:
            return "ds-empty"

        def get_data_source(self, data_source_id: str) -> dict:
            return {"title": [{"plain_text": "Empty DB"}]}

    class _DBResult:
        data_sources_exported = 1
        rows_exported = 0
        files_written = 0
        attachments_downloaded = 0
        warnings = []

    def fake_export_child_database(*, client, data_source_id, title, out_dir):
        return _DBResult()

    monkeypatch.setattr("noteshift.api.NotionClient", _Client)
    monkeypatch.setattr(
        "noteshift.api.export_child_database", fake_export_child_database
    )

    config = NoteshiftConfig(notion_token="t", out_dir=out_dir, overwrite=True)
    plan = ExportPlan(page_ids=[], database_ids=["db-empty"])

    res = run_export(plan, config)
    assert res.databases_exported == 1
    assert res.rows_exported == 0

    recon = _load_recon(out_dir)
    db_items = [i for i in recon["items"] if i["id"] == "ds-empty"]
    assert len(db_items) == 1

    db_item = db_items[0]
    assert db_item["status"] == "success"
    assert db_item["type"] == "database"
    assert db_item["title"] == "Empty DB"
    assert db_item.get("rows_exported") == 0
    assert db_item.get("files_written") == 0
