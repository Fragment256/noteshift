# Versioning and Release Policy

## Versioning model
`noteshift` follows Semantic Versioning.

- `MAJOR`: breaking CLI/API behavior changes
- `MINOR`: backward-compatible features
- `PATCH`: backward-compatible fixes/docs/internal improvements

## Tagging
Releases are triggered by pushing tags matching `v*`.

Examples:
- `v0.2.0`
- `v0.2.1`

## Release requirements
Before creating a tag:

1. update `CHANGELOG.md` from `[Unreleased]` into a version section
2. ensure CI is green on `main`
3. run local verification:
   - `uv run ruff format --check .`
   - `uv run ruff check .`
   - `uv run mypy src`
   - `uv run pytest --cov=noteshift --cov-report=term --cov-fail-under=65 tests`

## Automation
The release workflow performs:
- full quality gate checks
- package build via `uv build`
- artifact upload
- GitHub release creation with generated notes
- optional PyPI publish when `PYPI_TOKEN` is configured
