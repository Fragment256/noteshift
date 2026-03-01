# Migration report

Every successful run writes two report files:

- `migration_report.json`
- `migration_report.md`

## What it contains

The report summarizes counts such as:

- pages exported
- databases exported
- rows exported
- attachments downloaded
- files written
- warnings

## How to use it

- Treat warnings as a checklist for manual validation.
- Use the counts to confirm export completeness across re-runs.

If you need to restart a migration from scratch, use `--force` to discard the checkpoint.
