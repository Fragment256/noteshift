from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

ProgressEventType = Literal[
    "phase",
    "item_start",
    "item_done",
    "warning",
    "error",
    "checkpoint",
    "summary",
]


@dataclass(frozen=True)
class ProgressEvent:
    type: ProgressEventType
    id: str | None = None
    title: str | None = None
    message: str | None = None


ProgressSink = Callable[[ProgressEvent], None]
