from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from noteshift.filenames import FilenamePolicy, NameDeduper
from noteshift.notion import NotionClient


@dataclass
class DataSourceExportResult:
    data_sources_exported: int
    rows_exported: int
    files_written: int
    warnings: list[str]


def export_child_database(
    *,
    client: NotionClient,
    data_source_id: str,
    title: str,
    out_dir: Path,
) -> DataSourceExportResult:
    """Export a Notion child database as schema + rows.

    MVP:
    - schema.json from GET /data_sources/{id}
    - rows.jsonl from POST /data_sources/{id}/query

    No CSV yet (avoid dependencies). No view recreation.
    """

    policy = FilenamePolicy()
    deduper = NameDeduper()
    stem = deduper.dedupe(policy.slug(title or "database"))

    db_dir = out_dir / "databases" / stem
    db_dir.mkdir(parents=True, exist_ok=True)

    warnings: list[str] = []
    files_written = 0

    schema_path = db_dir / "schema.json"
    rows_path = db_dir / "rows.jsonl"

    try:
        schema = client.get_data_source(data_source_id)
        schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        files_written += 1
    except Exception as e:  # noqa: BLE001
        warnings.append(f"Failed to fetch schema for data source {data_source_id}: {e}")
        schema = None

    rows: list[dict] = []
    try:
        rows = client.query_data_source(data_source_id)
        with rows_path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, sort_keys=True))
                f.write("\n")
        files_written += 1
    except Exception as e:  # noqa: BLE001
        warnings.append(f"Failed to query data source {data_source_id}: {e}")

    # simple index note
    index_path = db_dir / "index.md"
    lines = [f"# {title}", "", f"Data source id: `{data_source_id}`", ""]
    if schema:
        lines.append("## Properties")
        props = schema.get("properties", {})
        for name, meta in props.items():
            ptype = meta.get("type") if isinstance(meta, dict) else ""
            lines.append(f"- **{name}** ({ptype})")
        lines.append("")
    lines.append(f"## Rows ({len(rows)})")
    lines.append("")
    lines.append("See `rows.jsonl` for full data.")
    index_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    files_written += 1

    return DataSourceExportResult(
        data_sources_exported=1,
        rows_exported=len(rows),
        files_written=files_written,
        warnings=warnings,
    )
