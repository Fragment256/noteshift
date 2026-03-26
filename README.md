# NoteShift (`noteshift`)

**NoteShift** exports Notion content to Obsidian-friendly Markdown with predictable filenames, link rewriting, and checkpoint/resume support.

[![CI](https://github.com/Fragment256/noteshift/actions/workflows/ci.yml/badge.svg)](https://github.com/Fragment256/noteshift/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/noteshift.svg)](https://pypi.org/project/noteshift/)
[![Python Versions](https://img.shields.io/pypi/pyversions/noteshift.svg)](https://pypi.org/project/noteshift/)
[![codecov](https://codecov.io/gh/Fragment256/noteshift/branch/main/graph/badge.svg)](https://codecov.io/gh/Fragment256/noteshift)

## Why it exists

Teams migrating from Notion to Obsidian consistently report four pains:

1. broken internal links after export
2. inconsistent filenames and folder layout
3. long exports failing midway without resume
4. low confidence in migration correctness

NoteShift is focused on solving those pains first.

## Current capabilities

- Export a Notion page tree to Markdown
- Export Notion data sources/databases through API layer
- Rewrite internal links for Obsidian compatibility
- Preserve and download attachments
- Resume interrupted runs via checkpoint file
- Emit migration report (`migration_report.json` + `.md`)
- Optionally emit YAML frontmatter with Notion metadata in each exported page

## Documentation

- Docs index: [`docs/`](docs/index.md)
- Start here: [Getting started](docs/getting-started.md)
- Library integration: [API contract](docs/api-contract.md)

## Installation

### Install from PyPI

```bash
uv tool install noteshift
# or
pipx install noteshift
```

### Install from source (development)

```bash
uv tool install .
uv sync --extra dev --extra test
```

## Authentication

Set a Notion integration token in `NOTION_TOKEN`.

```bash
export NOTION_TOKEN="secret_xxx"
```

## Basic usage

```bash
noteshift export \
  --page-id "<notion-page-id>" \
  --out ./export \
  --max-depth 2 \
  --overwrite
```

## Frontmatter

Pass `--frontmatter` to include YAML frontmatter at the top of every exported markdown file:

```bash
noteshift export \
  --page-id "<notion-page-id>" \
  --out ./export \
  --frontmatter
```

Each `index.md` will begin with a block like:

```yaml
---
notionId: "abc12345-..."
notionUrl: "https://www.notion.so/..."
createdAt: "2024-01-01T10:00:00.000Z"
updatedAt: "2024-06-15T14:30:00.000Z"
title: "My Page"
---
```

For pages that live inside a Notion database, supported property types are also included as additional keys (`select`, `multi_select`, `date`, `checkbox`, `number`, `url`, `email`, `phone_number`, `rich_text`). Property names are lowercased and spaces are replaced with underscores.

Frontmatter is off by default so existing exports are unaffected.

## Output

A successful run writes:

- Markdown files for exported pages
- downloaded assets in the export tree
- `.checkpoint.json` for resume
- `migration_report.json`
- `migration_report.md`

## Development

```bash
uv sync --extra dev --extra test
uv run ruff format .
uv run ruff check .
uv run mypy src
uv run pytest --cov=noteshift --cov-report=term
```

## Contract tests (`pytest-vcr`)

Contract tests are deterministic and replay HTTP traffic from sanitized cassettes:

```bash
uv run pytest -m contract
```

To re-record cassettes intentionally, set a real token in your environment and run:

```bash
VCR_RECORD_MODE=once uv run pytest -m contract
```

## License

MIT
