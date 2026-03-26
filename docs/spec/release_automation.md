# SPEC: Make releases part of CI (NoteShift)

## Decision
We use **release-please** to automate versioning, release PRs, and tagging on `main`.

## Why this choice
- Keeps changelog + version updates consistent.
- Removes manual "remember to tag" step.
- Works cleanly with existing tag-triggered release workflow.

## Triggering rules
- Conventional commits drive release categorization.
- release-please opens/updates a release PR.
- Merging the release PR creates tag `vX.Y.Z` + GitHub Release.
- Existing `Release` workflow handles build + PyPI publish.

## Guardrails
- CI checks version alignment between:
  - `pyproject.toml` (`project.version`)
  - `.release-please-manifest.json`
- Required quality gates remain enforced before merge.

## Acceptance criteria mapping
- Auto-tag + release on merge: ✅
- GitHub Release + PyPI publish path: ✅
- Documented maintainer flow: ✅ (`docs/release.md`)

## Test plan
1. Merge a patch-level change to `main`.
2. Confirm release-please PR is created/updated.
3. Merge release PR.
4. Verify:
   - tag exists (`vX.Y.Z`)
   - GitHub Release exists
   - PyPI version is published
