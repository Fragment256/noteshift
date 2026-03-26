from __future__ import annotations

from pathlib import Path

from noteshift.reconciliation import ReconciliationReport, write_reconciliation_report


def test_reconciliation_to_markdown_includes_sections() -> None:
    report = ReconciliationReport.create(is_resumed=True)
    report.add_success("p1", "page", title="Home")
    report.add_failure("p2", "page", "boom", title="Broken")
    report.add_skipped("p3", "page", "already exported")
    report.add_warning("warn-1")
    report.finalize()

    content = report.to_markdown()

    assert "# Reconciliation Report" in content
    assert "## Summary" in content
    assert "## Items by Status" in content
    assert "## Errors" in content
    assert "## Warnings" in content
    assert "**Resume:** Yes" in content


def test_write_reconciliation_report_writes_json_and_markdown(tmp_path: Path) -> None:
    report = ReconciliationReport.create(is_resumed=False)
    report.add_success("db-1", "database", title="Tasks")
    report.finalize()

    json_path = write_reconciliation_report(report, tmp_path)
    markdown_path = tmp_path / "reconciliation_report.md"

    assert json_path.exists()
    assert markdown_path.exists()
    assert "# Reconciliation Report" in markdown_path.read_text(encoding="utf-8")
