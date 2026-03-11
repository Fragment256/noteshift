# Release process

This repo publishes to **PyPI** via GitHub Actions **trusted publishing**.

The Release workflow is triggered by pushing a tag that matches `v*`.

## Prereqs

- You must land changes to `main` via a PR (branch protection).
- CI must be green (required checks).

## Step-by-step

1) **Merge the release PR**

Typical contents:
- Bump `project.version` in `pyproject.toml`
- Update `CHANGELOG.md`

2) **Create and push the tag**

From an up-to-date local `main`:

```bash
git checkout main
git pull

git tag vX.Y.Z
git push origin vX.Y.Z
```

3) **Watch the Release workflow**

GitHub Actions → Release

The job should:
- run quality gates (ruff / mypy / pytest + coverage threshold)
- build wheel + sdist
- create a GitHub Release with `dist/*` assets attached
- publish to PyPI

4) **Verify publication**

- GitHub Release exists: `https://github.com/Fragment256/noteshift/releases/tag/vX.Y.Z`
- PyPI shows the version: `https://pypi.org/project/noteshift/X.Y.Z/`

## Notes

- If PyPI is slow to show a new version, wait ~30–60s and refresh.
- If you see failures, check the workflow logs for the failing step.
