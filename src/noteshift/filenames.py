from __future__ import annotations

import re
from dataclasses import dataclass

from slugify import slugify

_INVALID_WINDOWS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1F]')


def _windows_safe(name: str) -> str:
    # Replace invalid chars with hyphen
    name = _INVALID_WINDOWS_CHARS.sub("-", name)
    # Strip trailing dots/spaces (Windows)
    name = name.rstrip(" .")
    return name


@dataclass
class FilenamePolicy:
    max_len: int = 100

    def slug(self, title: str) -> str:
        base = title.strip() or "untitled"
        base = _windows_safe(base)
        # slugify but keep readable
        s = slugify(base, separator="-", lowercase=False)
        s = s.strip("-") or "untitled"
        if len(s) > self.max_len:
            s = s[: self.max_len].rstrip("-")
        return s


class NameDeduper:
    def __init__(self) -> None:
        self._seen: dict[str, int] = {}

    def dedupe(self, stem: str) -> str:
        n = self._seen.get(stem, 0) + 1
        self._seen[stem] = n
        if n == 1:
            return stem
        return f"{stem}-{n}"
