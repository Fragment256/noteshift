# noteshift

`Notion exporter for seamless Obsidian migration.`

## 🚀 What is noteshift?

`noteshift` is a powerful command-line tool designed to facilitate the migration of your notes from Notion to Obsidian. It aims to provide a robust and efficient way to export your Notion pages and databases, preserving your data structure and content as closely as possible.

## ✨ MVP Features

*   **Page Export**: Export individual Notion pages and their content.
*   **Database Export**: Export Notion databases into a structured format suitable for Obsidian.
*   **Link Rewriting**: Automatically rewrites Notion internal links to Obsidian-compatible links.
*   **Attachments**: Handles image and file attachments, ensuring they are correctly exported and linked.
*   **Checkpoint/Resume**: Supports resuming interrupted migrations, saving progress and preventing data loss.
*   **Migration Reports**: Generates detailed reports on the migration process, highlighting successes and any encountered issues.

## 📦 Installation

You can install `noteshift` using `pip` or `uv` directly from its Git repository:

```bash
# Using pip
pip install git+https://github.com/yourusername/noteshift.git

# Using uv
# uv install git+https://github.com/yourusername/noteshift.git
```

*(Note: Replace `https://github.com/yourusername/noteshift.git` with the actual repository URL if different.)*

## 🔌 Environment Variables

`noteshift` requires your Notion API integration token to authenticate with the Notion API.

*   `NOTESHIFT_NOTION_TOKEN`: Your Notion Internal Integration Token.

Ensure this token is set in your environment before running the tool.

## 🎮 Basic Usage

Here's a simple example of how to use `noteshift` from your terminal:

```bash
export NOTESHIFT_NOTION_TOKEN="your_super_secret_token"
noteshift export --space-id "your_notion_space_id" --output-dir ./my-notion-export
```

This command will export your Notion content from the specified space ID to the `./my-notion-export` directory.

## 📁 Output Structure

Upon a successful export, `noteshift` will create a directory structure that mirrors your Notion hierarchy, with Markdown files (`.md`) for pages and associated assets (like images) placed alongside them. Database exports will be in a structured format (e.g., CSV or JSON) within the output directory.

## 🛠️ Development Setup

To set up `noteshift` for development, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/noteshift.git
    cd noteshift
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # or for uv:
    # uv venv
    # source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    # Using pip
pip install -e .[dev]

# Using uv
# uv sync --dev
```

*(Note: `.[dev]` or `--dev` assumes your `pyproject.toml` defines a `[project.optional-dependencies]` for development tools like linters, formatters, etc.)*

4.  **Run linters/formatters (optional but recommended)**:
    ```bash
    ruff check .
    ruff format .
    ```

Now you are ready to make changes and contribute!
