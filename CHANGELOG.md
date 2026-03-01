# Changelog

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
- Release workflow now builds artifacts, creates GitHub releases, and optionally publishes to PyPI
