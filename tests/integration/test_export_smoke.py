from __future__ import annotations

from pathlib import Path

from noteshift.api import run_export
from noteshift.types import ExportPlan, NoteshiftConfig


def test_run_export_writes_report_and_checkpoint(monkeypatch, tmp_path: Path) -> None:
    def fake_export_page_tree(**kwargs):
        checkpoint = kwargs["checkpoint"]
        checkpoint.add_page(kwargs["root_page_id"])
        checkpoint.add_file("root/index.md")
        return None

    monkeypatch.setattr("noteshift.api.export_page_tree", fake_export_page_tree)

    config = NoteshiftConfig(
        notion_token="test-token",
        out_dir=tmp_path / "out",
        overwrite=True,
    )
    plan = ExportPlan(page_ids=["root-page-id"], database_ids=[])

    result = run_export(plan, config)

    assert result.pages_exported == 1
    assert result.checkpoint_path is not None
    assert result.checkpoint_path.exists()
    assert result.report_path.exists()


def test_run_export_respects_fail_fast(monkeypatch, tmp_path: Path) -> None:
    def fake_export_page_tree(**_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("noteshift.api.export_page_tree", fake_export_page_tree)

    config = NoteshiftConfig(
        notion_token="test-token",
        out_dir=tmp_path / "out",
        overwrite=True,
        fail_fast=True,
    )
    plan = ExportPlan(page_ids=["root-page-id"], database_ids=[])

    try:
        run_export(plan, config)
    except RuntimeError as exc:
        assert "Failed to export page" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError in fail_fast mode")
