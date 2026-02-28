from __future__ import annotations

import os
from pathlib import Path

import typer

from noteshift.api import preflight, run_export
from noteshift.types import ExportPlan, NoteshiftConfig

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
        envvar="NOTION_TOKEN",
        help="Notion integration token. Also reads NOTION_TOKEN env var.",
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

    token = notion_token or os.getenv("NOTION_TOKEN") or ""
    out = out.resolve()

    config = NoteshiftConfig(
        notion_token=token,
        out_dir=out,
        overwrite=overwrite,
        force=force,
        max_depth=max_depth,
        license_key=license_key,
    )
    plan = ExportPlan(page_ids=[page_id], database_ids=[])

    report = preflight(plan, config)
    if not report.ok:
        raise typer.BadParameter("; ".join(report.errors))

    if force:
        typer.echo("Force mode enabled. Discarding previous checkpoint.")
    else:
        typer.echo(f"Loading checkpoint from {out / '.checkpoint.json'}")

    typer.echo(f"NoteShift exporting page tree {page_id} to {out}")

    if license_key:
        typer.echo("License activated: Unlimited depth enabled")
    else:
        typer.echo(f"Free tier: Maximum depth is {max_depth} levels. Use --license-key for unlimited.")

    result = run_export(plan=plan, config=config)

    typer.echo("\nMigration Report")
    typer.echo("----------------")
    typer.echo(f"Pages exported: {result.pages_exported}")
    typer.echo(f"Databases exported: {result.databases_exported}")
    typer.echo(f"Rows exported: {result.rows_exported}")
    typer.echo(f"Attachments downloaded: {result.attachments_downloaded}")

    if result.warnings:
        typer.echo("\nWarnings")
        for warning in result.warnings:
            typer.echo(f"- {warning}")

    typer.echo(f"\nJSON report saved to {result.report_path}")
    typer.echo(f"Checkpoint saved to {result.checkpoint_path}")

    if result.errors:
        typer.echo("\nErrors")
        for error in result.errors:
            typer.echo(f"- {error}", err=True)
        typer.echo("\nExport failed with errors.", err=True)
        raise typer.Exit(code=1)

    typer.echo("\nExport complete.")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
