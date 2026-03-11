# SPEC: Make releases part of CI (NoteShift)

## Problem
Releases require manual steps (bump version, merge, then remember to create/push a tag). When tagging is forgotten, GitHub Release + PyPI publication don’t happen.

## Goal
Make releases *reliably* happen as part of our normal workflow, with guardrails:
- version bumps are intentional
- release automation is repeatable
- CI enforces readiness (tests/lint/typecheck + coverage)

Non-goals:
- redesign packaging
- change user-facing CLI

## Current state
- `CI` workflow runs on PRs/pushes and gates merges.
- `Release` workflow runs only on `push` of tags matching `v*`.

## Options
### A) Keep tag-triggered release, but enforce the tag
- Keep the current Release workflow.
- Add a CI check on `main` merges that detects `pyproject.toml` version bump without a corresponding tag, and fails with instructions.
- Pros: simplest, minimal change.
- Cons: still manual tagging; still room for “oops”.

### B) Auto-tag + release on merge (recommended)
- Use a release automation tool to:
  - detect version changes / conventional commits
  - create tag + GitHub Release
  - trigger existing `Release` workflow (or replace it)
- Candidates:
  - **release-please** (Google)
  - python-semantic-release
- Pros: no manual tagging; consistent.
- Cons: introduces new tool/config.

### C) Manual “workflow_dispatch” release
- Add a button-triggered workflow (`workflow_dispatch`) that tags and releases.
- Pros: less automation complexity than fully automatic.
- Cons: still relies on someone clicking.

## Recommendation
Option **B**: auto-tag + release on merge (release-please or python-semantic-release).

## Acceptance criteria
- Merging a release PR results in:
  - a new tag `vX.Y.Z`
  - a GitHub Release with wheel+sdist assets
  - PyPI shows the new version
- CI remains the merge gate.
- Documented release flow exists in `docs/release.md`.

## Test plan
- Merge a small patch bump.
- Verify:
  - tag exists
  - GitHub Release page
  - `pip install noteshift==X.Y.Z` works in a clean venv
