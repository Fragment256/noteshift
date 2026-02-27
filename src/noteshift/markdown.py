from __future__ import annotations

from collections.abc import Iterable


def rich_text_plain(rich_text: list[dict] | None) -> str:
    if not rich_text:
        return ""
    parts: list[str] = []
    for rt in rich_text:
        if rt.get("type") == "text":
            parts.append(rt.get("text", {}).get("content", ""))
        else:
            # fallback: attempt common field
            parts.append(rt.get(rt.get("type"), {}).get("content", ""))
    return "".join(parts)


def md_escape(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def indent_lines(lines: Iterable[str], prefix: str) -> list[str]:
    return [prefix + ln if ln else ln for ln in lines]


def render_toggle(summary: str, body_lines: list[str]) -> list[str]:
    # Obsidian renders <details> HTML fine.
    out: list[str] = []
    out.append(f"<details><summary>{md_escape(summary)}</summary>")
    out.append("")
    out.extend(body_lines)
    out.append("")
    out.append("</details>")
    return out
