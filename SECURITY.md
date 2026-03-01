# Security Policy

## Reporting a vulnerability

Please do **not** open a public issue for security vulnerabilities.

Report privately to the maintainers with:

- affected version/commit
- impact summary
- reproduction steps
- suggested mitigation (if known)

## Secrets and test artifacts

- Never commit Notion tokens.
- `pytest-vcr` cassettes must be sanitized.
- Pull requests containing secrets will be rejected.
