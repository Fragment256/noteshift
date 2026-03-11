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
    """

    id: str
    item_type: str
    status: str  # 'success', 'failed', 'skipped'
    title: str | None = None
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "type": self.item_type,
            "status": self.status,
            "title": self.title,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReconciliationItem:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            item_type=data["type"],
            status=data["status"],
            title=data.get("title"),
            message=data.get("message"),
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
        self, item_id: str, item_type: str, title: str | None = None
    ) -> None:
        """Record a successful item export.

        Args:
            item_id: Unique identifier for the item
            item_type: Type of item (page, database, etc.)
            title: Optional title of the item
        """
        self.items.append(
            ReconciliationItem(
                id=item_id,
                item_type=item_type,
                status="success",
                title=title,
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


def write_reconciliation_report(report: ReconciliationReport, out_dir: Path) -> Path:
    """Write the reconciliation report to disk.

    The report is written to a fixed path: {out_dir}/reconciliation_report.json

    Args:
        report: The reconciliation report to write
        out_dir: Output directory for the report file

    Returns:
        Path to the written report file
    """
    report_path = out_dir / "reconciliation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report.to_json(), encoding="utf-8")
    return report_path


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
