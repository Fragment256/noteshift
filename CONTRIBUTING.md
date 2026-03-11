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
- Keep or improve test coverage.
- PRs should keep the **Codecov patch** check green (diff coverage meets target).
- Reviewers: treat a failing coverage check as a merge blocker unless there’s a documented reason.

## Contract tests

`pytest-vcr` cassettes must be sanitized. Never commit live tokens or private identifiers.
