from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC
from pathlib import Path
from typing import Any


@dataclass
class Checkpoint:
    """Tracks export progress for resumable exports."""

    version: int = 1
    timestamp: str = ""
    # IDs of exported items
    page_ids: set[str] = field(default_factory=set)
    database_ids: set[str] = field(default_factory=set)
    # Files written (relative paths from out_dir)
    files_written: list[str] = field(default_factory=list)
    # Statistics
    attachments_downloaded: int = 0
    rows_exported: int = 0
    # Warnings accumulated
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> Checkpoint:
        """Load checkpoint from file, or return empty if not exists."""
        if not path.exists():
            return cls()
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return cls(
                version=data.get("version", 1),
                timestamp=data.get("timestamp", ""),
                page_ids=set(data.get("page_ids", [])),
                database_ids=set(data.get("database_ids", [])),
                files_written=data.get("files_written", []),
                attachments_downloaded=data.get("attachments_downloaded", 0),
                rows_exported=data.get("rows_exported", 0),
                warnings=data.get("warnings", []),
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return cls()

    def save(self, path: Path) -> None:
        """Save checkpoint to file."""
        from datetime import datetime

        self.timestamp = datetime.now(UTC).isoformat()
        data = {
            "version": self.version,
            "timestamp": self.timestamp,
            "page_ids": sorted(self.page_ids),
            "database_ids": sorted(self.database_ids),
            "files_written": self.files_written,
            "attachments_downloaded": self.attachments_downloaded,
            "rows_exported": self.rows_exported,
            "warnings": self.warnings,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def is_page_exported(self, page_id: str) -> bool:
        return page_id in self.page_ids

    def is_database_exported(self, db_id: str) -> bool:
        return db_id in self.database_ids

    def add_page(self, page_id: str) -> None:
        self.page_ids.add(page_id)

    def add_database(self, db_id: str) -> None:
        self.database_ids.add(db_id)

    def add_file(self, rel_path: str) -> None:
        if rel_path not in self.files_written:
            self.files_written.append(rel_path)

    def add_attachment(self) -> None:
        self.attachments_downloaded += 1

    def add_rows(self, count: int) -> None:
        self.rows_exported += count

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)

    def get_stats(self) -> dict[str, Any]:
        return {
            "pages_exported": len(self.page_ids),
            "databases_exported": len(self.database_ids),
            "files_written": len(self.files_written),
            "attachments_downloaded": self.attachments_downloaded,
            "rows_exported": self.rows_exported,
            "warnings_count": len(self.warnings),
        }
