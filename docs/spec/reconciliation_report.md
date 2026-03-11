# SPEC: Reconciliation report (export completeness + actionable errors)

## Goal
Give users a reliable, machine-readable + human-readable summary of what exported, what failed, and what needs manual attention.

## Non-goals
- No new export formats.
- No UI changes (CLI/library only).

## Requirements (must)
- Produce **JSON** report with:
  - counts: pages exported, blocks processed, databases exported, attachments attempted/downloaded/failed
  - lists: failures (with error types), warnings (e.g. link rewrite anomalies), skipped items
  - timing: start/end/duration
  - resume: whether checkpoint/resume was used
- Produce **Markdown** report for humans.
- Report path is deterministic (existing `migration_report.*` is fine; otherwise `reconciliation_report.*`).
- Tests:
  - unit tests for report schema generation
  - integration smoke test verifying files created

## Acceptance criteria
- `uv run pytest tests/` passes.
- Running export (with fixtures/mocks) creates both reports.

## Issue breakdown
- Reconciliation: core schema + JSON writer
- Reconciliation: Markdown writer
- Reconciliation: attachment status tracking
- Reconciliation: database export summary
- Reconciliation: warnings/errors capture plumbing
- Tests: unit + integration for report outputs
