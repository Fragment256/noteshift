# Filenames + link rewriting

## Goals

- **Predictable filenames** so exported notes are stable across runs
- **Obsidian-compatible internal links** so navigation works after migration

## Filenames

noteshift slugifies titles and ensures uniqueness.

If you see collisions (two pages with the same title), noteshift will disambiguate filenames.

## Link rewriting

Notion internal links are rewritten to point at the exported Markdown notes.

If you find a link that did not rewrite correctly:

1. Check the migration report warnings
2. Confirm both source pages were included in your export scope
3. Re-run the export (resume will be fast) after adjusting scope
