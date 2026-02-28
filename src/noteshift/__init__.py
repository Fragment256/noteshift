from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "__version__",
    "ExportPlan",
    "ExportResult",
    "NoteshiftConfig",
    "PreflightReport",
    "ProgressEvent",
    "ProgressSink",
    "preflight",
    "run_export",
]

__version__ = "0.1.0"


def __getattr__(name: str) -> Any:
    if name in {"ExportPlan", "ExportResult", "NoteshiftConfig", "PreflightReport"}:
        return getattr(import_module("noteshift.types"), name)
    if name in {"ProgressEvent", "ProgressSink"}:
        return getattr(import_module("noteshift.events"), name)
    if name in {"preflight", "run_export"}:
        return getattr(import_module("noteshift.api"), name)
    raise AttributeError(f"module 'noteshift' has no attribute {name!r}")
