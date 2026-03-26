# Production Readiness Spec (Public Release)

This spec defines what “production-ready” means for **Noteshift** and provides a checklist for a public OSS release.

## Definition: production-ready
Noteshift is production-ready when it meets:

1) **Stability**
- Core export flows behave predictably.
- Failures are actionable (clear error messages).
- Resume/checkpoint works reliably.

2) **Usability**
- Clean install via PyPI.
- Quickstart works as written.
- Docs match `noteshift --help`.

3) **Maintainability**
- Tests exist and run in CI.
- `uv` is used for installs/build/test.
- `ruff` lint/format is enforced.

4) **Security**
- No secrets are logged or written to disk.
- A vulnerability reporting process exists (`SECURITY.md`).

5) **Distribution**
- Wheel + sdist build reliably.
- Tag-based release workflow is verified.
- PyPI trusted publishing is proven end-to-end.

## Release gate (v0.1.x)
Must-have items are tracked as issues in the Production Readiness project.

### Must-have (v0.1.0)
- PyPI metadata cleanup (no placeholders)
- README public-release pass
- CLI reference doc (`docs/cli.md`)
- Verify trusted publishing release end-to-end
- LICENSE consistency
- SECURITY.md
- CI enforces ruff
- API stable surface + contract tests
- (Optional) CI mypy wiring

## PR discipline
- No direct pushes to `main`.
- All work via branch → PR.
- PR descriptions must include auto-close keywords when applicable, e.g. `Closes #36`.
