from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class ReconciliationItem:
    """A single item in the reconciliation report.

    Attributes:
        id: Unique identifier for the item
        item_type: Type of item (page, database, row, etc.)
        status: Status of the item (success, failed, skipped)
        title: Optional title of the item
        message: Optional message (error or info)
        rows_exported: For databases, number of rows exported
        files_written: For databases, number of files written
    """

    id: str
    item_type: str
    status: str  # 'success', 'failed', 'skipped'
    title: str | None = None
    message: str | None = None
    rows_exported: int = 0
    files_written: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        result: dict[str, Any] = {
            "id": self.id,
            "type": self.item_type,
            "status": self.status,
            "title": self.title,
            "message": self.message,
        }
        # Add database-specific fields if non-zero
        if self.rows_exported > 0:
            result["rows_exported"] = self.rows_exported
        if self.files_written > 0:
            result["files_written"] = self.files_written
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReconciliationItem:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            item_type=data["type"],
            status=data["status"],
            title=data.get("title"),
            message=data.get("message"),
            rows_exported=data.get("rows_exported", 0),
            files_written=data.get("files_written", 0),
        )


@dataclass
class ReconciliationReport:
    """Reconciliation report for an export run.

    This schema tracks the complete state of an export operation,
    including timing, resume status, and per-item results.

    Attributes:
        version: Schema version (for future migrations)
        started_at: ISO timestamp when export started
        completed_at: ISO timestamp when export completed
        is_resumed: Whether this was a resume from a previous checkpoint
        total_items: Total number of items processed
        success_count: Number of items successfully exported
        failed_count: Number of items that failed
        skipped_count: Number of items skipped (already exported)
        items: Detailed list of all items and their status
        errors: Summary list of error messages
        warnings: Summary list of warnings
    """

    version: int = 1
    started_at: str = ""
    completed_at: str = ""
    is_resumed: bool = False
    total_items: int = 0
    success_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    items: list[ReconciliationItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, is_resumed: bool = False) -> ReconciliationReport:
        """Create a new report with current timestamp.

        Args:
            is_resumed: Whether this export is resuming from a checkpoint

        Returns:
            New ReconciliationReport instance
        """
        return cls(
            version=1,
            started_at=datetime.now(UTC).isoformat(),
            is_resumed=is_resumed,
        )

    def add_success(
        self,
        item_id: str,
        item_type: str,
        title: str | None = None,
        rows_exported: int = 0,
        files_written: int = 0,
    ) -> None:
        """Record a successful item export.

        Args:
            item_id: Unique identifier for the item
            item_type: Type of item (page, database, etc.)
            title: Optional title of the item
            rows_exported: Number of rows exported (for databases)
            files_written: Number of files written (for databases)
        """
        self.items.append(
            ReconciliationItem(
                id=item_id,
                item_type=item_type,
                status="success",
                title=title,
                rows_exported=rows_exported,
                files_written=files_written,
            )
        )
        self.success_count += 1
        self.total_items += 1

    def add_failure(
        self, item_id: str, item_type: str, error: str, title: str | None = None
    ) -> None:
        """Record a failed item export.

        Args:
            item_id: Unique identifier for the item
            item_type: Type of item (page, database, etc.)
            error: Error message describing the failure
            title: Optional title of the item
        """
        self.items.append(
            ReconciliationItem(
                id=item_id,
                item_type=item_type,
                status="failed",
                title=title,
                message=error,
            )
        )
        self.errors.append(f"{item_type} {item_id}: {error}")
        self.failed_count += 1
        self.total_items += 1

    def add_skipped(
        self, item_id: str, item_type: str, reason: str = "already exported"
    ) -> None:
        """Record a skipped item (already exported from checkpoint).

        Args:
            item_id: Unique identifier for the item
            item_type: Type of item (page, database, etc.)
            reason: Reason for skipping (default: "already exported")
        """
        self.items.append(
            ReconciliationItem(
                id=item_id,
                item_type=item_type,
                status="skipped",
                message=reason,
            )
        )
        self.skipped_count += 1
        self.total_items += 1

    def add_warning(self, warning: str) -> None:
        """Add a warning message to the report.

        Args:
            warning: Warning message
        """
        self.warnings.append(warning)

    def finalize(self) -> None:
        """Mark the report as complete with the current timestamp."""
        self.completed_at = datetime.now(UTC).isoformat()

    def get_stats(self) -> dict[str, Any]:
        """Get summary statistics.

        Returns:
            Dictionary with count statistics
        """
        return {
            "total": self.total_items,
            "success": self.success_count,
            "failed": self.failed_count,
            "skipped": self.skipped_count,
            "is_resumed": self.is_resumed,
            "duration_seconds": self._calculate_duration(),
        }

    def _calculate_duration(self) -> float | None:
        """Calculate duration in seconds, or None if not completed."""
        if not self.started_at or not self.completed_at:
            return None
        try:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            return (end - start).total_seconds()
        except (ValueError, TypeError):
            return None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the report to a dictionary.

        Returns:
            Dictionary representation of the report
        """
        return {
            "version": self.version,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "is_resumed": self.is_resumed,
            "counts": {
                "total": self.total_items,
                "success": self.success_count,
                "failed": self.failed_count,
                "skipped": self.skipped_count,
            },
            "items": [item.to_dict() for item in self.items],
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.get_stats(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReconciliationReport:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing report data

        Returns:
            ReconciliationReport instance
        """
        counts = data.get("counts", {})
        items_data = data.get("items", [])
        items = [ReconciliationItem.from_dict(item) for item in items_data]

        return cls(
            version=data.get("version", 1),
            started_at=data.get("started_at", ""),
            completed_at=data.get("completed_at", ""),
            is_resumed=data.get("is_resumed", False),
            total_items=counts.get("total", len(items)),
            success_count=counts.get("success", 0),
            failed_count=counts.get("failed", 0),
            skipped_count=counts.get("skipped", 0),
            items=items,
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
        )

    def to_json(self) -> str:
        """Serialize to JSON string.

        Returns:
            JSON representation of the report
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def to_markdown(self) -> str:
        """Serialize to human-friendly markdown format.

        Returns:
            Markdown representation of the report
        """
        lines = [
            "# Reconciliation Report",
            "",
            f"**Export Date:** {self.started_at}",
            f"**Duration:** {self._format_duration()}",
            f"**Resume:** {'Yes' if self.is_resumed else 'No'}",
            "",
            "## Summary",
            "",
            f"- **Total Items:** {self.total_items}",
            f"- **Successful:** {self.success_count}",
            f"- **Failed:** {self.failed_count}",
            f"- **Skipped:** {self.skipped_count}",
            "",
        ]

        # Group items by status
        if self.items:
            lines.append("## Items by Status")
            lines.append("")

            # Sort items by status and then by id
            sorted_items = sorted(self.items, key=lambda x: (x.status, x.id))

            for item in sorted_items:
                title_str = f" ({item.title})" if item.title else ""
                lines.append(f"- **{item.id}**{title_str}")
                lines.append(f"  - Type: {item.item_type}")
                lines.append(f"  - Status: {item.status}")
                if item.message:
                    lines.append(f"  - Message: {item.message}")
                lines.append("")

        # Errors section
        if self.errors:
            lines.append("## Errors")
            lines.append("")
            for error in self.errors:
                lines.append(f"- {error}")
            lines.append("")

        # Warnings section
        if self.warnings:
            lines.append("## Warnings")
            lines.append("")
            for warning in self.warnings:
                lines.append(f"- {warning}")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def _format_duration(self) -> str:
        """Format the export duration as a human-readable string."""
        if not self.completed_at or not self.started_at:
            return "N/A"
        try:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            duration = end - start
            seconds = int(duration.total_seconds())
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            if hours > 0:
                return f"{hours}h {minutes}m {secs}s"
            if minutes > 0:
                return f"{minutes}m {secs}s"
            return f"{secs}s"
        except (ValueError, TypeError):
            return "N/A"


def write_reconciliation_report(report: ReconciliationReport, out_dir: Path) -> Path:
    """Write the reconciliation report to disk in both JSON and Markdown formats.

    The reports are written to:
    - {out_dir}/reconciliation_report.json (machine-readable)
    - {out_dir}/reconciliation_report.md (human-readable)

    Args:
        report: The reconciliation report to write
        out_dir: Output directory for the report files

    Returns:
        Path to the JSON report file (for backward compatibility)
    """
    # Write JSON version
    json_path = out_dir / "reconciliation_report.json"
    markdown_path = out_dir / "reconciliation_report.md"

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(report.to_json(), encoding="utf-8")
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")

    return json_path


def load_reconciliation_report(path: Path) -> ReconciliationReport | None:
    """Load a reconciliation report from disk.

    Args:
        path: Path to the report file

    Returns:
        ReconciliationReport instance, or None if file doesn't exist
    """
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return ReconciliationReport.from_dict(data)
    except (json.JSONDecodeError, KeyError, TypeError):
        return None
