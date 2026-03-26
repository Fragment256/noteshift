# SPEC: YAML Frontmatter with Notion Metadata

## Goal

Optionally emit YAML frontmatter in exported markdown files containing Notion page metadata (ID, URL, timestamps, and database properties).

## Non-goals

- Writing metadata back to Notion (round-trip sync)
- Custom frontmatter templates or user-defined field mapping
- Frontmatter in database row exports (`.jsonl` files already have full metadata)

## Users / scenario

- Users exporting Notion pages to feed into static site generators (Hugo, Jekyll, Astro, Eleventy) that consume YAML frontmatter
- Users who want traceability back to the source Notion page after export
- Users building automation on top of exported markdown who need stable IDs

## Requirements (must)

- [ ] New `--frontmatter` CLI flag (off by default) to enable frontmatter generation
- [ ] Corresponding `frontmatter: bool` field on `NoteshiftConfig`
- [ ] When enabled, each `index.md` starts with a YAML frontmatter block containing: `notionId`, `notionUrl`, `createdAt`, `updatedAt`, `title`
- [ ] For pages that live in a Notion database, include all database properties as additional frontmatter keys (text, select, multi-select, date, checkbox, number, url, email, phone)
- [ ] Frontmatter is valid YAML parseable by PyYAML / any standard YAML parser
- [ ] Existing behaviour unchanged when `--frontmatter` is not passed

## Nice-to-haves

- [ ] `--frontmatter-fields` option to cherry-pick which fields to include
- [ ] Map Notion `relation` and `rollup` property types to frontmatter

## Acceptance criteria (definition of done)

- [ ] `noteshift export --page-id ... --frontmatter` produces markdown with valid YAML frontmatter
- [ ] Frontmatter contains `notionId`, `notionUrl`, `createdAt`, `updatedAt`, `title`
- [ ] Database properties appear as extra keys when the page belongs to a database
- [ ] Without `--frontmatter`, output is identical to current behaviour (no regression)
- [ ] Unit tests cover frontmatter generation for standalone pages and database pages
- [ ] Integration/contract test verifies frontmatter from a real Notion API response cassette
- [ ] 80%+ test coverage on new code

## Risks / constraints

- Notion page objects may not always include `url` (e.g. bot lacks "Read content" capability) -- handle gracefully with `null`
- Property type mapping needs to handle edge cases (empty multi-select, formula results, etc.)
- Adding `pyyaml` as a dependency vs hand-rolling YAML -- PyYAML is safer for correctness

## Issue breakdown

1. **Add frontmatter generation module** (`src/noteshift/frontmatter.py`)
2. **Wire frontmatter into export pipeline**
3. **Add `--frontmatter` CLI flag**
4. **Map Notion database properties to frontmatter**

## PR discipline

- Branch -> PR only
- PR body includes: `Closes #...` for each issue
- Commands to run (paste output in PR):
  - `ruff check src/ tests/`
  - `black --check src/ tests/`
  - `pytest --cov=src --cov-report=term-missing`
