from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import typer

from noteshift.checkpoint import Checkpoint
from noteshift.exporter import export_page_tree

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def export(
    page_id: str = typer.Option(
        ..., "--page-id", help="Root Notion page ID to export (UUID with or without dashes)."
    ),
    out: Path = typer.Option(
        Path("./out"), "--out", help="Output directory (will be created)."
    ),
    notion_token: str | None = typer.Option(
        None,
        "--notion-token",
        envvar="NOTESHIFT_NOTION_TOKEN",
        help="Notion integration token. Also reads NOTESHIFT_NOTION_TOKEN env var.",
    ),
    force: bool = typer.Option(
        False, "--force", help="Force re-export of all items, ignoring checkpoint."
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Allow overwriting output directory even if not empty."
    ),
    max_depth: int = typer.Option(
        2, "--max-depth", help="Maximum depth to export (free tier: 2, unlimited with license key)."
    ),
    license_key: str | None = typer.Option(
        None,
        "--license-key",
        envvar="NOTESHIFT_LICENSE_KEY",
        help="License key for unlimited depth and advanced features.",
    ),
):
    """Export a Notion page tree to Markdown (MVP: structure + toggles/children preserved)."""

    token = notion_token or os.getenv("NOTION_TOKEN")
    if not token:
        raise typer.BadParameter(
            "Missing Notion token. Provide with --notion-token or set NOTESHIFT_NOTION_TOKEN."
        )

    out = out.resolve()
    if out.exists() and any(out.iterdir()) and not overwrite:
        raise typer.BadParameter(
            f"Output dir {out} is not empty. Use --overwrite or pick a new --out."
        )
    out.mkdir(parents=True, exist_ok=True)

    checkpoint_path = out / ".checkpoint.json"
    checkpoint = Checkpoint.load(checkpoint_path)

    if force:
        checkpoint = Checkpoint()
        typer.echo("Force mode enabled. Discarding previous checkpoint.")
    else:
        typer.echo(f"Loading checkpoint from {checkpoint_path}")

    typer.echo(f"NoteShift exporting page tree {page_id} to {out}")

    if license_key:
        typer.echo("License activated: Unlimited depth enabled")
    else:
        typer.echo(f"Free tier: Maximum depth is {max_depth} levels. Use --license-key for unlimited.")
    
    export_page_tree(
        token=token,
        root_page_id=page_id,
        out_dir=out,
        checkpoint=checkpoint,
        force=force,
        license_key=license_key,
        max_depth=max_depth,
    )

    checkpoint.save(checkpoint_path)

    typer.echo("\nMigration Report")
    typer.echo("----------------")
    typer.echo(f"Pages exported: {len(checkpoint.page_ids)}")
    typer.echo(f"Databases exported: {len(checkpoint.database_ids)}")
    typer.echo(f"Rows exported: {checkpoint.rows_exported}")
    typer.echo(f"Attachments downloaded: {checkpoint.attachments_downloaded}")
    typer.echo(f"Files written: {len(checkpoint.files_written)}")
    if checkpoint.warnings:
        typer.echo("\nWarnings")
        for w in checkpoint.warnings:
            typer.echo(f"- {w}")

    # --- Migration Report Generation ---
    report_data = {
        "timestamp": datetime.now(UTC).isoformat(),
        "pages_exported_total": len(checkpoint.page_ids),
        "databases_exported_total": len(checkpoint.database_ids),
        "rows_exported_total": checkpoint.rows_exported,
        "attachments_downloaded_total": checkpoint.attachments_downloaded,
        "files_written_total": len(checkpoint.files_written),
        "warnings": checkpoint.warnings,
    }

    # JSON Report
    json_report_path = out / "migration_report.json"
    try:
        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        typer.echo(f"\nJSON report saved to {json_report_path}")
    except Exception as e:
        typer.echo(f"Error saving JSON report: {e}", err=True)

    # Markdown Report
    md_report_path = out / "migration_report.md"
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
        f"| Attachments Downloaded | {report_data['attachments_downloaded_total']} |",
        f"| Files Written | {report_data['files_written_total']} |",
        "",
        "## Warnings",
        "",
    ]
    if report_data["warnings"]:
        for warning in report_data["warnings"]:
            md_lines.append(f"- {warning}")
    else:
        md_lines.append("No warnings.")

    try:
        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines) + "\n")
        typer.echo(f"Markdown report saved to {md_report_path}")
    except Exception as e:
        typer.echo(f"Error saving Markdown report: {e}", err=True)

    typer.echo("\nExport complete.")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
