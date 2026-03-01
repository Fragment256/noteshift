# Release Checklist

## Pre-release
- [ ] `uv sync --extra dev --extra test`
- [ ] `uv run ruff format --check .`
- [ ] `uv run ruff check .`
- [ ] `uv run mypy src`
- [ ] `uv run pytest --cov=noteshift --cov-report=term`
- [ ] Contract tests pass (`uv run pytest -m contract`)
- [ ] README examples verified
- [ ] CHANGELOG updated

## Tag and release
- [ ] bump version in `pyproject.toml`
- [ ] create git tag `vX.Y.Z`
- [ ] push tag and verify release workflow
- [ ] publish release notes

## Post-release
- [ ] smoke test install from released artifact
- [ ] verify docs and badges reference latest release
