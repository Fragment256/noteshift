from __future__ import annotations

from collections.abc import Iterable
from typing import Callable


def rich_text_to_markdown(
    rich_text: list[dict] | None,
    page_mapper: Callable[[str], str | None] | None = None,
) -> str:
    """Convert Notion rich text to Markdown with link rewriting.

    Handles:
    - text with annotations (bold, italic, code)
    - internal page mentions (rewritten to relative links via page_mapper)
    - external URLs
    """
    if not rich_text:
        return ""
    parts: list[str] = []
    for rt in rich_text:
        text_content = ""
        is_link = False
        link_url = ""

        rt_type = rt.get("type")

        if rt_type == "text":
            text_obj = rt.get("text", {})
            text_content = text_obj.get("content", "")
            link = text_obj.get("link")
            if link:
                is_link = True
                link_url = link.get("url", "")
        elif rt_type == "mention":
            mention = rt.get("mention", {})
            mention_type = mention.get("type")
            if mention_type == "page":
                page_id = mention.get("page", {}).get("id", "")
                # Try to get page title from plain_text, fallback to shortened ID
                text_content = rt.get("plain_text", "")
                if not text_content:
                    text_content = f"@{page_id[:8]}..."
                if page_mapper:
                    mapped = page_mapper(page_id)
                    if mapped:
                        is_link = True
                        link_url = mapped
            elif mention_type == "user":
                user_name = rt.get("plain_text", "")
                text_content = user_name or "@user"
            elif mention_type == "date":
                date_info = mention.get("date", {})
                start = date_info.get("start", "")
                text_content = start or rt.get("plain_text", "")
            elif mention_type == "database":
                db_id = mention.get("database", {}).get("id", "")
                text_content = rt.get("plain_text", "") or f"db:{db_id[:8]}..."
            else:
                text_content = rt.get("plain_text", "")
        else:
            # Fallback for other types
            text_content = rt.get("plain_text", "")

        # Apply annotations (bold, italic, strikethrough, code)
        annotations = rt.get("annotations", {})
        if annotations.get("code"):
            text_content = f"`{text_content}`"
        if annotations.get("bold"):
            text_content = f"**{text_content}**"
        if annotations.get("italic"):
            text_content = f"*{text_content}*"
        if annotations.get("strikethrough"):
            text_content = f"~~{text_content}~~"

        if is_link and link_url:
            # Escape pipe characters in link text for Obsidian compatibility
            safe_text = text_content.replace("|", "\\|")
            parts.append(f"[{safe_text}]({link_url})")
        else:
            parts.append(text_content)

    return "".join(parts)


def rich_text_plain(rich_text: list[dict] | None) -> str:
    """Extract plain text from rich_text (fallback for non-link contexts)."""
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
