# SPEC: PyPI publish verification via tag (Noteshift)

## Goal
Prove (end-to-end) that tagging a release publishes `noteshift` to PyPI and that strangers can install and run it.

## Non-goals
- No feature work.
- No GUI work.

## Current state
- Release workflow exists: `.github/workflows/release.yml` uses `uv build` + `uv publish --trusted-publishing=always` on tag `v*`.
- We have **not** conclusively verified PyPI publishing end-to-end.

## Requirements (must)
- A tag (e.g. `v0.1.0` or `v0.1.1`) triggers GitHub Actions Release workflow.
- Workflow successfully publishes artifacts to **PyPI**.
- Fresh environment install succeeds:
  - `pipx install noteshift` OR `uv tool install noteshift`
  - `noteshift --help` runs
- Document the exact release steps in `docs/release.md`.

## Acceptance criteria (definition of done)
- PyPI has the released version.
- GitHub Release exists with wheel+sdist attached.
- A clean install (no repo checkout) can run `noteshift --help`.

## Risks / constraints
- Trusted publishing requires **PyPI-side configuration** (publisher mapping to this repo/workflow).
- Branch protection / required checks can block merges, but tag triggers should still run.

## Issue breakdown
- PyPI: configure trusted publishing for `noteshift`
- Release: cut tag + verify Actions run
- Verify install: clean machine/venv installs from PyPI and runs
- Docs: write `docs/release.md`

