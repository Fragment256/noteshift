# Concepts

## What NoteShift exports

NoteShift exports Notion content to Obsidian-friendly Markdown.

Two primary export sources:

- **Page tree**: a root page and its child pages (up to `max_depth`)
- **Database**: a Notion database / data source exported via the Notion API layer

## Checkpoint / resume

Exports can be long-running. NoteShift writes a `.checkpoint.json` file in the output directory.

- If an export is interrupted, running the same export again will resume using the checkpoint.
- Use `--force` (or `force=True` in the library config) to start fresh.

## Output layout

The output directory contains:

- Markdown files (pages)
- A folder tree reflecting the exported structure
- Downloaded assets (attachments)
- Migration report files (`migration_report.json` and `migration_report.md`)

## Library API

If you are integrating noteshift into another tool (e.g., a GUI), use the library API:

- `noteshift.types.ExportPlan`
- `noteshift.types.NoteshiftConfig`
- `noteshift.api.run_export(plan, config, progress=...)`
