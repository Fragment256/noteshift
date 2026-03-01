# noteshift

`noteshift` exports Notion content to Obsidian-friendly Markdown with predictable filenames, link rewriting, and checkpoint/resume support.

![CI](https://github.com/Fragment256/noteshift/actions/workflows/ci.yml/badge.svg)

## Why it exists

Teams migrating from Notion to Obsidian consistently report four pains:

1. broken internal links after export
2. inconsistent filenames and folder layout
3. long exports failing midway without resume
4. low confidence in migration correctness

`noteshift` is focused on solving those pains first.

## Current capabilities

- Export a Notion page tree to Markdown
- Export Notion data sources/databases through API layer
- Rewrite internal links for Obsidian compatibility
- Preserve and download attachments
- Resume interrupted runs via checkpoint file
- Emit migration report (`migration_report.json` + `.md`)

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

## Roadmap and readiness

Readiness work is tracked in GitHub issues:

- Epic: transfer + production/open-source readiness
- OSS baseline docs and metadata
- CI hardening
- customer-pain validation matrix
- contract/e2e test expansion

## License

MIT
