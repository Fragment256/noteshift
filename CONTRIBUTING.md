# Contributing to noteshift

## Setup

```bash
uv sync --extra dev --extra test
```

## Quality bar

Before opening a PR:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy src
uv run pytest --cov=noteshift --cov-report=term
```

## Pull requests

- Keep PRs focused and small.
- Reference linked issue(s).
- Include tests for behavior changes.
- Update docs for any CLI/API changes.

## Contract tests

`pytest-vcr` cassettes must be sanitized. Never commit live tokens or private identifiers.
