# Release process

Releases are automated with **release-please** on `main`.

## How it works

1. Pushes to `main` run `.github/workflows/release-please.yml`.
2. release-please opens/updates a release PR with:
   - version bump in `pyproject.toml`
   - changelog updates
3. When that release PR is merged, release-please creates a tag (`vX.Y.Z`) and GitHub Release.
4. The tag triggers `.github/workflows/release.yml`, which:
   - runs quality gates
   - builds artifacts
   - publishes to PyPI via trusted publishing

## Maintainer flow

1) Merge normal feature/fix PRs into `main`.

2) Wait for release-please to open/update the release PR.

3) Review and merge the release PR.

4) Verify automation:
- GitHub Release exists: `https://github.com/Fragment256/noteshift/releases`
- PyPI shows the new version: `https://pypi.org/project/noteshift/`

## Guardrails

CI validates release metadata alignment between:
- `pyproject.toml` project version
- `.release-please-manifest.json`

If these drift, CI fails with an actionable error.

## Required secret

Configure repository secret:

- `RELEASE_PLEASE_TOKEN`: a fine-grained PAT (or bot token) with permissions to:
  - read/write repository contents
  - read/write pull requests

This token is used so release-please-created PRs reliably trigger CI checks.

## Notes

- Do **not** manually edit version numbers on random PRs.
- Use release-please flow so changelog, tags, and releases stay consistent.
