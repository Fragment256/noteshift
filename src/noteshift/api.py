from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from noteshift.checkpoint import Checkpoint
from noteshift.db_export import export_child_database
from noteshift.events import ProgressEvent, ProgressSink
from noteshift.exporter import export_page_tree
from noteshift.notion import NotionClient
from noteshift.reconciliation import ReconciliationReport
from noteshift.types import ExportPlan, ExportResult, NoteshiftConfig, PreflightReport


def _emit(progress: ProgressSink | None, event: ProgressEvent) -> None:
    if progress is not None:
        progress(event)


def _write_migration_report(
    out_dir: Path, checkpoint: Checkpoint
) -> tuple[Path, list[str]]:
    report_errors: list[str] = []
    report_data: dict[str, object] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "pages_exported_total": len(checkpoint.page_ids),
        "databases_exported_total": len(checkpoint.database_ids),
        "rows_exported_total": checkpoint.rows_exported,
        "attachments_downloaded_total": checkpoint.attachments_downloaded,
        "files_written_total": len(checkpoint.files_written),
        "warnings": checkpoint.warnings,
    }

    json_report_path = out_dir / "migration_report.json"
    try:
        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        md_report_path = out_dir / "migration_report.md"
        md_lines = [
            "# Migration Report",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "| :----- | :---- |",
            f"| Timestamp | {report_data['timestamp']} |",
            f"| Pages Exported | {report_data['pages_exported_total']} |",
            f"| Databases Exported | {report_data['databases_exported_total']} |",
            f"| Rows Exported | {report_data['rows_exported_total']} |",
            (
                "| Attachments Downloaded | "
                f"{report_data['attachments_downloaded_total']} |"
            ),
            f"| Files Written | {report_data['files_written_total']} |",
            "",
            "## Warnings",
            "",
        ]
        warnings = report_data["warnings"]
        if isinstance(warnings, list) and warnings:
            for warning in warnings:
                md_lines.append(f"- {warning}")
        else:
            md_lines.append("No warnings.")

        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines) + "\n")
    except OSError as exc:
        report_errors.append(f"Failed to write migration report files: {exc}")

    return json_report_path, report_errors


def _database_title(schema: dict) -> str:
    title_obj = schema.get("title")
    if isinstance(title_obj, list) and title_obj:
        first = title_obj[0]
        if isinstance(first, dict) and first.get("plain_text"):
            return str(first["plain_text"])
    return "Database"


def preflight(plan: ExportPlan, config: NoteshiftConfig) -> PreflightReport:
    errors: list[str] = []
    warnings: list[str] = []

    token = config.notion_token or os.getenv("NOTION_TOKEN")
    if not token:
        errors.append(
            "Missing Notion token. Provide config.notion_token or set NOTION_TOKEN."
        )

    if not plan.page_ids and not plan.database_ids:
        errors.append(
            "Export plan is empty. Provide at least one page_id or database_id."
        )

    if config.max_depth < 0:
        errors.append("max_depth must be >= 0.")

    out_dir = config.out_dir.resolve()
    if out_dir.exists():
        if not out_dir.is_dir():
            errors.append(
                f"Output path {out_dir} exists and is not a directory. "
                "Choose a directory path for out_dir."
            )
        elif any(out_dir.iterdir()) and not config.overwrite:
            errors.append(
                f"Output dir {out_dir} is not empty. "
                "Use overwrite=True or choose a new out_dir."
            )

    return PreflightReport(ok=not errors, errors=errors, warnings=warnings)


def run_export(
    plan: ExportPlan,
    config: NoteshiftConfig,
    progress: ProgressSink | None = None,
) -> ExportResult:
    report = preflight(plan, config)
    if not report.ok:
        raise ValueError("; ".join(report.errors))

    token = config.notion_token or os.getenv("NOTION_TOKEN")
    if token is None:
        raise ValueError("Missing Notion token.")

    out_dir = config.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_path = out_dir / ".checkpoint.json"
    checkpoint = Checkpoint.load(checkpoint_path)

    # Initialize reconciliation report (issue #50)
    recon_report = ReconciliationReport.create(is_resumed=bool(checkpoint.timestamp))

    _emit(progress, ProgressEvent(type="phase", message="starting_export"))

    # Check for items already exported from checkpoint (resumed export)
    for page_id in checkpoint.page_ids:
        if page_id in plan.page_ids:
            recon_report.add_skipped(page_id, "page", "already exported (checkpoint)")

    for db_id in checkpoint.database_ids:
        if db_id in plan.database_ids:
            recon_report.add_skipped(db_id, "database", "already exported (checkpoint)")

    for page_id in plan.page_ids:
        if page_id in checkpoint.page_ids:
            continue  # Skip already exported (already recorded above)

        _emit(progress, ProgressEvent(type="item_start", id=page_id, title="page"))
        try:
            export_page_tree(
                token=token,
                root_page_id=page_id,
                out_dir=out_dir,
                checkpoint=checkpoint,
                force=config.force,
                max_depth=config.max_depth,
            )
            recon_report.add_success(page_id, "page")
            _emit(progress, ProgressEvent(type="item_done", id=page_id, title="page"))
        except Exception as exc:  # noqa: BLE001
            msg = f"Failed to export page {page_id}: {exc}"
            recon_report.add_failure(page_id, "page", msg)
            _emit(
                progress,
                ProgressEvent(type="error", id=page_id, title="page", message=msg),
            )
            if config.fail_fast:
                # Save checkpoint and finalize reconciliation report before raising
                checkpoint.save(checkpoint_path)
                recon_report.finalize()
                recon_path = out_dir / "reconciliation_report.json"
                recon_path.write_text(recon_report.to_json(), encoding="utf-8")
                raise RuntimeError(msg) from exc

    if plan.database_ids:
        client = NotionClient(token)
        for database_id in plan.database_ids:
            # Skip if already exported via checkpoint
            try:
                resolved_id = client.resolve_data_source_id(database_id)
            except Exception:
                resolved_id = database_id  # Fallback

            if resolved_id in checkpoint.database_ids:
                # Record as skipped (resumed export) even if the plan uses a
                # database_id and the checkpoint stores the resolved data_source_id.
                recon_report.add_skipped(
                    resolved_id,
                    "database",
                    "already exported (checkpoint)",
                )
                continue

            _emit(
                progress,
                ProgressEvent(type="item_start", id=database_id, title="database"),
            )
            try:
                data_source_id = client.resolve_data_source_id(database_id)
                schema = client.get_data_source(data_source_id)
                title = _database_title(schema)
                db_result = export_child_database(
                    client=client,
                    data_source_id=data_source_id,
                    title=title,
                    out_dir=out_dir,
                )
                checkpoint.add_database(data_source_id)
                checkpoint.add_rows(db_result.rows_exported)

                # Record success in reconciliation report
                recon_report.add_success(data_source_id, "database", title=title)

                for warning in db_result.warnings:
                    checkpoint.add_warning(warning)
                    recon_report.add_warning(warning)
                    _emit(
                        progress,
                        ProgressEvent(
                            type="warning",
                            id=data_source_id,
                            title="database",
                            message=warning,
                        ),
                    )
                _emit(
                    progress,
                    ProgressEvent(
                        type="item_done", id=data_source_id, title="database"
                    ),
                )
            except Exception as exc:  # noqa: BLE001
                msg = f"Failed to export database {database_id}: {exc}"
                recon_report.add_failure(database_id, "database", msg)
                _emit(
                    progress,
                    ProgressEvent(
                        type="error", id=database_id, title="database", message=msg
                    ),
                )
                if config.fail_fast:
                    # Save checkpoint and finalize reconciliation report before raising
                    checkpoint.save(checkpoint_path)
                    recon_report.finalize()
                    recon_path = out_dir / "reconciliation_report.json"
                    recon_path.write_text(recon_report.to_json(), encoding="utf-8")
                    raise RuntimeError(msg) from exc

    checkpoint.save(checkpoint_path)
    _emit(progress, ProgressEvent(type="checkpoint", message=str(checkpoint_path)))

    # Finalize + write reconciliation report
    recon_report.finalize()
    from noteshift.reconciliation import write_reconciliation_report

    recon_path = write_reconciliation_report(recon_report, out_dir)

    report_path, report_errors = _write_migration_report(out_dir, checkpoint)

    summary = ExportResult(
        out_dir=out_dir,
        report_path=report_path,
        checkpoint_path=checkpoint_path,
        pages_exported=len(checkpoint.page_ids),
        databases_exported=len(checkpoint.database_ids),
        rows_exported=checkpoint.rows_exported,
        attachments_attempted=checkpoint.attachments_attempted,
        attachments_downloaded=checkpoint.attachments_downloaded,
        attachments_failed=checkpoint.attachments_failed,
        warnings=list(checkpoint.warnings),
        errors=recon_report.errors + report_errors,
    )

    _emit(
        progress,
        ProgressEvent(
            type="summary",
            message=(
                f"pages={summary.pages_exported}, "
                f"databases={summary.databases_exported}, "
                f"rows={summary.rows_exported}, "
                f"attachments="
                f"({summary.attachments_attempted} attempted, "
                f"{summary.attachments_downloaded} downloaded, "
                f"{summary.attachments_failed} failed)"
            ),
        ),
    )

    return summary
