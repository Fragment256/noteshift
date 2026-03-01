# Getting started

## 1) Create a Notion integration token

Create a Notion integration and copy its token.

Set it in your environment:

```bash
export NOTION_TOKEN="secret_xxx"
```

## 2) Install NoteShift

### Using uv (recommended)

```bash
uv tool install noteshift
```

### Using pipx

```bash
pipx install noteshift
```

> If you are developing locally, see the project README for `uv sync` and dev extras.

## 3) Run your first export (page tree)

```bash
noteshift export \
  --page-id "<notion-page-id>" \
  --out ./export \
  --max-depth 2 \
  --overwrite
```

## 4) What you get

A successful run writes:

- Markdown files for exported pages
- Downloaded assets inside the export tree
- `.checkpoint.json` (resume support)
- `migration_report.json`
- `migration_report.md`

Next:
- Learn the available flags in the [CLI reference](cli.md)
- Understand checkpoints and export scope in [Concepts](concepts.md)
