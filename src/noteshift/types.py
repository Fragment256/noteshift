from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class NoteshiftConfig:
    notion_token: str
    out_dir: Path
    overwrite: bool = False
    force: bool = False
    max_depth: int = 2
    license_key: str | None = None


@dataclass(frozen=True)
class ExportPlan:
    page_ids: list[str] = field(default_factory=list)
    database_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PreflightReport:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExportResult:
    out_dir: Path
    report_path: Path
    checkpoint_path: Path | None
    pages_exported: int
    databases_exported: int
    rows_exported: int
    attachments_downloaded: int
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
