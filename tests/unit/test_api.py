from __future__ import annotations

from pathlib import Path

import pytest

from noteshift.api import preflight, run_export
from noteshift.types import ExportPlan, NoteshiftConfig


def test_preflight_requires_token_and_inputs(tmp_path: Path) -> None:
    config = NoteshiftConfig(notion_token="", out_dir=tmp_path / "out")
    plan = ExportPlan(page_ids=[], database_ids=[])

    report = preflight(plan, config)

    assert report.ok is False
    assert any("Missing Notion token" in err for err in report.errors)
    assert any("Export plan is empty" in err for err in report.errors)


def test_run_export_validation_errors(tmp_path: Path) -> None:
    config = NoteshiftConfig(notion_token="", out_dir=tmp_path / "out")
    plan = ExportPlan(page_ids=[], database_ids=[])

    with pytest.raises(ValueError, match="Missing Notion token"):
        run_export(plan, config)


def test_run_export_emits_progress_events(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    events: list[str] = []

    def fake_export_page_tree(**_kwargs):
        checkpoint = _kwargs["checkpoint"]
        checkpoint.add_page(_kwargs["root_page_id"])
        checkpoint.add_file("root/index.md")
        return None

    monkeypatch.setattr("noteshift.api.export_page_tree", fake_export_page_tree)

    config = NoteshiftConfig(
        notion_token="test-token",
        out_dir=tmp_path / "out",
        overwrite=True,
    )
    plan = ExportPlan(page_ids=["root-page-id"], database_ids=[])

    result = run_export(plan, config, progress=lambda e: events.append(e.type))

    assert result.pages_exported == 1
    assert "phase" in events
    assert "item_start" in events
    assert "item_done" in events
    assert "checkpoint" in events
    assert "summary" in events
