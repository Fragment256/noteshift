# Releasing the noteshift package

This document outlines the process for releasing new versions of the noteshift Python package using GitHub Actions and PyPI's trusted publishing.

## Prerequisites

*   You must have write access to the Fragment256/noteshift repository.
*   A GitHub Actions release workflow must be triggered with a tag starting with `v` (e.g., `v1.0.0`).

## Release Process

1.  **Create a new tag:**
    ```bash
    git tag vX.Y.Z  # Replace X.Y.Z with the new version number
    git push origin vX.Y.Z
    ```
    This will automatically trigger the release workflow.

2.  **Monitor the GitHub Actions workflow:**
    Navigate to the "Actions" tab in the repository to monitor the progress of the `Release` workflow. The workflow performs the following steps:
    *   Checks out the code.
    *   Sets up Python and installs dependencies.
    *   Runs quality gates (formatting, linting, type checking, and tests).
    *   Builds the package distributions (`sdist` and `wheel`) into the `dist/` directory.
    *   Uploads the distribution artifacts to GitHub Releases.
    *   Creates a GitHub Release with auto-generated release notes based on the changelog.
    *   **Publishes the package to PyPI using trusted publishing.** This step uses OIDC to authenticate with PyPI, eliminating the need for manual API tokens.

## PyPI Trusted Publishing Configuration

The repository is configured to use PyPI's trusted publishing. This means that GitHub Actions can obtain short-lived OIDC tokens to authenticate with PyPI.

**Important:** The GitHub repository `Fragment256/noteshift` has been configured with the necessary OIDC settings on PyPI. No manual PyPI configuration is required on your part if you are a maintainer of this repository.

If you encounter issues with publishing, ensure the following:

*   The GitHub repository has the `id-token: write` permission enabled for the `Release` workflow.
*   The `release.yml` workflow correctly uses the `pypa/gh-action-pypi-publish` action, which handles the OIDC authentication flow.

## Troubleshooting

If the release fails during the PyPI publishing step, double-check the workflow logs for specific error messages. Common issues include:

*   Incorrect package name in `pyproject.toml`.
*   Network issues preventing communication with PyPI.
*   Recent changes in PyPI's OIDC requirements.

Closes #58
