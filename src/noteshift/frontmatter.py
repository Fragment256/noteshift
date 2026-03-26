from __future__ import annotations

import re


# Property types we know how to extract a scalar/list value from.
_SUPPORTED_PROPERTY_TYPES = frozenset(
    {
        "rich_text",
        "select",
        "multi_select",
        "date",
        "checkbox",
        "number",
        "url",
        "email",
        "phone_number",
    }
)


def _slugify_key(name: str) -> str:
    """Convert a Notion property name to a safe YAML key (snake_case)."""
    lowered = name.lower()
    # Replace any non-alphanumeric run with a single underscore
    return re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")


def _yaml_value(value: object) -> str:
    """Serialise a Python value to a YAML scalar / inline sequence."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        if not value:
            return "[]"
        items = ", ".join(f'"{str(v)}"' for v in value)
        return f"[{items}]"
    # String — always double-quote and escape inner double-quotes
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _extract_property_value(prop: dict) -> object:
    """Extract a Python-native value from a Notion property dict."""
    ptype = prop.get("type")

    if ptype == "rich_text":
        text = _plain_text_from_rich_text(prop.get("rich_text") or [])
        return text or None

    if ptype == "select":
        sel = prop.get("select")
        return sel["name"] if sel else None

    if ptype == "multi_select":
        items = prop.get("multi_select") or []
        return [item["name"] for item in items]

    if ptype == "date":
        date_obj = prop.get("date")
        return date_obj["start"] if date_obj else None

    if ptype == "checkbox":
        return bool(prop.get("checkbox"))

    if ptype == "number":
        return prop.get("number")

    if ptype == "url":
        return prop.get("url")

    if ptype == "email":
        return prop.get("email")

    if ptype == "phone_number":
        return prop.get("phone_number")

    return None  # unsupported type sentinel (caller skips it)


def _plain_text_from_rich_text(rich_text: list[dict]) -> str:
    """Extract plain text from a Notion rich_text array.

    Handles both real API format (``plain_text`` field) and mock format
    (``text.content`` field).
    """
    parts: list[str] = []
    for chunk in rich_text:
        if "plain_text" in chunk:
            parts.append(chunk["plain_text"])
        elif chunk.get("type") == "text":
            parts.append(chunk.get("text", {}).get("content", ""))
        else:
            parts.append(chunk.get(chunk.get("type", ""), {}).get("content", ""))
    return "".join(parts)


def _page_title_from_properties(properties: dict) -> str:
    """Return the plain-text title from a Notion page properties dict."""
    for prop in properties.values():
        if isinstance(prop, dict) and prop.get("type") == "title":
            return _plain_text_from_rich_text(prop.get("title") or [])
    return "Untitled"


def build_frontmatter(page: dict) -> str:
    """Build a YAML frontmatter string from a Notion page API object.

    Returns a string of the form::

        ---
        notionId: "..."
        notionUrl: "..."
        createdAt: "..."
        updatedAt: "..."
        title: "..."
        [... database properties ...]
        ---

    All values are present; missing optional fields are rendered as ``null``.
    """
    properties = page.get("properties") or {}
    title = _page_title_from_properties(properties)

    lines: list[str] = [
        "---",
        f"notionId: {_yaml_value(page.get('id'))}",
        f"notionUrl: {_yaml_value(page.get('url'))}",
        f"createdAt: {_yaml_value(page.get('created_time'))}",
        f"updatedAt: {_yaml_value(page.get('last_edited_time'))}",
        f"title: {_yaml_value(title)}",
    ]

    for name, prop in properties.items():
        if not isinstance(prop, dict):
            continue
        ptype = prop.get("type")
        if ptype == "title":
            # Already emitted as the "title" core field
            continue
        if ptype not in _SUPPORTED_PROPERTY_TYPES:
            continue
        key = _slugify_key(name)
        value = _extract_property_value(prop)
        lines.append(f"{key}: {_yaml_value(value)}")

    lines.append("---")
    return "\n".join(lines) + "\n"
