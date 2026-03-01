# Customer Pain Map

## Scope
This document maps concrete migration pain to implemented capabilities, tests, and acceptance criteria.

## Pain 1: Internal links break after migration
- Capability: internal Notion link rewriting to Obsidian-friendly links
- Acceptance criteria:
  - links between exported pages resolve to generated markdown targets
  - no raw Notion URL remains where resolvable target exists
- Validation:
  - unit tests in markdown/link rewrite paths
  - export integration snapshot checks (#11)

## Pain 2: Output naming/layout is inconsistent
- Capability: deterministic filename normalization and stable folder layout
- Acceptance criteria:
  - repeated exports of same content generate identical paths
  - illegal filename characters are normalized
- Validation:
  - unit tests for filename normalization
  - integration snapshot checks (#11)

## Pain 3: Long migrations fail midway with no resume
- Capability: checkpoint save/load and resume behavior
- Acceptance criteria:
  - interrupted run can continue without re-exporting completed items
  - force mode intentionally resets checkpoint behavior
- Validation:
  - checkpoint unit tests
  - integration/e2e interruption simulation (#11)

## Pain 4: Teams cannot trust migration correctness
- Capability: migration report + deterministic tests (unit, contract, integration)
- Acceptance criteria:
  - each export emits summary metrics and warnings/errors
  - CI fails on regressions
- Validation:
  - unit tests
  - pytest-vcr contract tests (#10)
  - integration/e2e smoke tests (#11)
