# API contract (library)

This page documents the public Python API intended for consumers such as `noteshift-gui`.

## Stable entry point

- `noteshift.api.run_export(plan, config, progress=None) -> noteshift.types.ExportResult`

### Inputs

- `noteshift.types.ExportPlan`
  - `page_ids: list[str]` — zero or more root page IDs
  - `database_ids: list[str]` — zero or more database/data source IDs
- `noteshift.types.NoteshiftConfig`
  - `notion_token: str`
  - `out_dir: Path`
  - `overwrite: bool`
  - `force: bool`
  - `max_depth: int`
  - `fail_fast: bool`

### Output

- `noteshift.types.ExportResult` — summary counts, paths, warnings, errors.

## Progress events

`run_export()` may emit `noteshift.events.ProgressEvent` objects to the provided `progress` callback.

### Event types (stable)

`ProgressEvent.type` is one of:

- `phase` — major phase transitions (e.g. starting)
- `item_start` — export of a single item is starting
- `item_done` — export of a single item completed successfully
- `warning` — non-fatal warning (should be shown to user)
- `error` — item-level failure (may be non-fatal unless `fail_fast=True`)
- `checkpoint` — checkpoint file saved
- `summary` — final summary message

### Field expectations

- `item_start`, `item_done`, `warning`, `error`:
  - `id` is set to the item ID
  - `title` is set to `page` or `database`
- `phase`, `checkpoint`, `summary`:
  - `message` is set

### Ordering invariants (best-effort)

- A run emits a `phase` event with `message="starting_export"` before any `item_start` events.
- For each item that completes successfully, `item_start` is followed by `item_done` with the same `id`.
- For each item that fails, an `error` event is emitted with the same `id`.
- A `summary` event is emitted at the end of a run.

> Note: The library is free to add new event types in a future major version.
