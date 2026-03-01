# Fragment256 Transfer Plan

## Goal
Move canonical repository ownership from `lukemaxwell/noteshift` to `Fragment256/noteshift` with no workflow downtime.

## Steps
1. Transfer repository ownership in GitHub settings (preferred over re-create).
2. Re-confirm admin/write permissions for maintainers and teams.
3. Validate branch protections on `main`.
4. Verify GitHub Actions secrets and environment protections.
5. Update badges/URLs/package metadata to Fragment256 URLs.
6. Update local remotes:
   - `git remote set-url origin git@github.com:Fragment256/noteshift.git`
7. Run CI on a no-op PR to confirm post-transfer health.

## Verification
- All workflows green after transfer.
- Existing open issues/PRs retained.
- README, metadata, and release links point to Fragment256 only.
