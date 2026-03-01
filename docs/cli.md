# CLI reference

## Command overview

- `noteshift export`: export one or more page trees and/or databases

Run:

```bash
noteshift --help
noteshift export --help
```

## Exporting pages

```bash
noteshift export \
  --page-id "<page-id>" \
  --out ./export \
  --max-depth 2 \
  --overwrite
```

## Exporting databases

```bash
noteshift export \
  --database-id "<database-id>" \
  --out ./export \
  --overwrite
```

## Exporting multiple sources in one run

You can repeat `--page-id` and `--database-id`.

```bash
noteshift export \
  --page-id "<page-id-1>" \
  --page-id "<page-id-2>" \
  --database-id "<db-id-1>" \
  --out ./export \
  --overwrite
```

## Common flags (high level)

- `--out`: output directory
- `--overwrite`: allow writing into a non-empty output directory
- `--max-depth`: max depth when exporting a page tree

See also:
- [Concepts](concepts.md)
- [Filenames + link rewriting](filenames-and-links.md)
