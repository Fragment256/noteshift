from __future__ import annotations

import os
from pathlib import Path

import typer
from rich.console import Console

from noteshift.exporter import export_page_tree

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


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
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Allow overwriting output directory even if not empty."
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

    console.print(f"[bold]NoteShift[/bold] exporting page tree {page_id} to {out}")
    result = export_page_tree(token=token, root_page_id=page_id, out_dir=out)

    console.print("\n[bold]Done[/bold]")
    console.print(f"Pages exported: {result.pages_exported}")
    console.print(f"Files written:  {result.files_written}")
    if result.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for w in result.warnings:
            console.print(f"- {w}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
