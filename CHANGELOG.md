# Changelog

## [0.1.4](https://github.com/Fragment256/noteshift/compare/v0.1.3...v0.1.4) (2026-03-11)


### Bug Fixes

* Address CRA feedback for PR [#77](https://github.com/Fragment256/noteshift/issues/77) (issue [#53](https://github.com/Fragment256/noteshift/issues/53)) ([#80](https://github.com/Fragment256/noteshift/issues/80)) ([8381390](https://github.com/Fragment256/noteshift/commit/8381390841aa6fce220ce5b7cae23ad2658f1df4))


### Documentation

* add release process ([#69](https://github.com/Fragment256/noteshift/issues/69)) ([4a2e68d](https://github.com/Fragment256/noteshift/commit/4a2e68d97c7ef8492f48510820b4d1b2b797fb40))

## [0.1.3] - 2026-03-11
- Fix: resolve Notion inline database IDs (database_id → data_source_id) so DB rows export correctly on Notion API 2025-09-03+.
- Fix: render bookmark blocks as Markdown links.
- Tests: add unit coverage for resolution paths and bookmark rendering.

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project aims to follow Semantic Versioning.

## [Unreleased]

### Added
- OSS baseline docs (`LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`)
- Initial pytest-vcr contract harness scaffolding
- Customer pain map and release checklist docs
- Versioning policy documentation (`docs/spec/versioning_policy.md`)

### Changed
- Refreshed README to reflect current CLI behavior and env vars
- Hardened CI to include formatting, blocking mypy, and stronger coverage gate
- Expanded deterministic contract and integration smoke validation
- Adopted release-please automation for release PR, tagging, and GitHub release flow
- Release workflow builds artifacts and publishes to PyPI via trusted publishing
