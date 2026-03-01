from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from noteshift.cli import app
from noteshift.types import ExportPlan, ExportResult, PreflightReport

runner = CliRunner()


def _ok_result(tmp_path: Path) -> ExportResult:
    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "migration_report.json"
    report_path.write_text("{}", encoding="utf-8")
    checkpoint_path = out_dir / ".checkpoint.json"
    checkpoint_path.write_text("{}", encoding="utf-8")
    return ExportResult(
        out_dir=out_dir,
        report_path=report_path,
        checkpoint_path=checkpoint_path,
        pages_exported=1,
        databases_exported=0,
        rows_exported=0,
        attachments_downloaded=0,
        warnings=[],
        errors=[],
    )


def test_export_success(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "noteshift.cli.preflight",
        lambda _plan, _config: PreflightReport(ok=True),
    )
    monkeypatch.setattr(
        "noteshift.cli.run_export", lambda **_kwargs: _ok_result(tmp_path)
    )

    result = runner.invoke(
        app,
        [
            "--page-id",
            "page-1",
            "--out",
            str(tmp_path / "out"),
            "--notion-token",
            "secret",
        ],
    )

    assert result.exit_code == 0
    assert "Export complete." in result.output
    assert "Pages exported: 1" in result.output


def test_export_preflight_failure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "noteshift.cli.preflight",
        lambda _plan, _config: PreflightReport(ok=False, errors=["bad input"]),
    )

    result = runner.invoke(
        app,
        [
            "--page-id",
            "page-1",
            "--out",
            str(tmp_path / "out"),
            "--notion-token",
            "secret",
        ],
    )

    assert result.exit_code != 0
    assert "bad input" in result.output


def test_export_force_mode_message(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "noteshift.cli.preflight",
        lambda _plan, _config: PreflightReport(ok=True),
    )
    monkeypatch.setattr(
        "noteshift.cli.run_export", lambda **_kwargs: _ok_result(tmp_path)
    )

    result = runner.invoke(
        app,
        [
            "--page-id",
            "page-1",
            "--out",
            str(tmp_path / "out"),
            "--notion-token",
            "secret",
            "--force",
        ],
    )

    assert result.exit_code == 0
    assert "Force mode enabled" in result.output


def test_export_errors_exit_nonzero(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "noteshift.cli.preflight",
        lambda _plan, _config: PreflightReport(ok=True),
    )

    def failed_result(**_kwargs) -> ExportResult:
        result = _ok_result(tmp_path)
        result.errors = ["failure one"]
        return result

    monkeypatch.setattr("noteshift.cli.run_export", failed_result)

    result = runner.invoke(
        app,
        [
            "--page-id",
            "page-1",
            "--out",
            str(tmp_path / "out"),
            "--notion-token",
            "secret",
        ],
    )

    assert result.exit_code == 1
    assert "Export failed with errors." in result.output


def test_export_shows_warnings(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "noteshift.cli.preflight",
        lambda _plan, _config: PreflightReport(ok=True),
    )

    def warned_result(**_kwargs) -> ExportResult:
        result = _ok_result(tmp_path)
        result.warnings = ["warn one"]
        return result

    monkeypatch.setattr("noteshift.cli.run_export", warned_result)

    result = runner.invoke(
        app,
        [
            "--page-id",
            "page-1",
            "--out",
            str(tmp_path / "out"),
            "--notion-token",
            "secret",
        ],
    )

    assert result.exit_code == 0
    assert "Warnings" in result.output
    assert "warn one" in result.output


def test_export_rejects_empty_plan(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "--out",
            str(tmp_path / "out"),
            "--notion-token",
            "secret",
        ],
    )

    assert result.exit_code != 0
    assert "Export plan is empty" in result.output


def test_export_multiple_page_and_database_ids(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def ok_preflight(plan, _config):  # type: ignore[no-untyped-def]
        captured["plan"] = plan
        return PreflightReport(ok=True)

    def ok_run_export(**kwargs):  # type: ignore[no-untyped-def]
        captured["kwargs"] = kwargs
        return _ok_result(tmp_path)

    monkeypatch.setattr("noteshift.cli.preflight", ok_preflight)
    monkeypatch.setattr("noteshift.cli.run_export", ok_run_export)

    result = runner.invoke(
        app,
        [
            "--page-id",
            "page-1",
            "--page-id",
            "page-2",
            "--database-id",
            "db-1",
            "--out",
            str(tmp_path / "out"),
            "--notion-token",
            "secret",
        ],
    )

    assert result.exit_code == 0
    plan = captured["plan"]
    assert isinstance(plan, ExportPlan)
    assert plan.page_ids == ["page-1", "page-2"]
    assert plan.database_ids == ["db-1"]
