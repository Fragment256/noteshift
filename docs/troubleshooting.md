# Troubleshooting

## Missing token / auth errors

Set `NOTION_TOKEN`:

```bash
export NOTION_TOKEN="secret_xxx"
```

## Output directory is not empty

Use `--overwrite` or choose a new output directory.

## Export is interrupted

Re-run the same command: noteshift will resume using `.checkpoint.json`.

To start fresh, use `--force`.

## Rate limits / transient API failures

- Re-run (resume should skip already-exported items).
- Consider exporting fewer sources at once.

## Links not rewriting as expected

- Confirm both pages are in the export scope.
- Check warnings in `migration_report.md`.
