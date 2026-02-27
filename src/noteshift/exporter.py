from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from noteshift.filenames import FilenamePolicy, NameDeduper
from noteshift.markdown import indent_lines, render_toggle, rich_text_plain
from noteshift.notion import NotionClient


@dataclass
class ExportResult:
    pages_exported: int
    files_written: int
    warnings: list[str]


def _page_title(page: dict) -> str:
    props = page.get("properties", {})
    # Title property can be named anything; find the first with type 'title'
    for v in props.values():
        if isinstance(v, dict) and v.get("type") == "title":
            return rich_text_plain(v.get("title"))
    return "Untitled"


def export_page_tree(*, token: str, root_page_id: str, out_dir: Path) -> ExportResult:
    client = NotionClient(token)
    policy = FilenamePolicy()
    deduper = NameDeduper()

    root = client.get_page(root_page_id)
    title = _page_title(root)
    stem = deduper.dedupe(policy.slug(title))
    md_path = out_dir / f"{stem}.md"

    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")

    blocks = client.list_block_children(root_page_id)
    lines.extend(_render_blocks(client, blocks, indent=""))

    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    # MVP only exports the root page for now; recursion comes next milestone.
    return ExportResult(pages_exported=1, files_written=1, warnings=[])


def _render_blocks(client: NotionClient, blocks: list[dict], indent: str) -> list[str]:
    out: list[str] = []

    for b in blocks:
        btype = b.get("type")
        payload = b.get(btype, {}) if btype else {}

        if btype == "paragraph":
            text = rich_text_plain(payload.get("rich_text"))
            if text:
                out.append(indent + text)
                out.append("")

        elif btype in {"heading_1", "heading_2", "heading_3"}:
            level = {"heading_1": "#", "heading_2": "##", "heading_3": "###"}[btype]
            text = rich_text_plain(payload.get("rich_text"))
            out.append(indent + f"{level} {text}")
            out.append("")

        elif btype == "bulleted_list_item":
            text = rich_text_plain(payload.get("rich_text"))
            out.append(indent + f"- {text}")
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                out.extend(indent_lines(_render_blocks(client, children, indent=""), indent + "  "))

        elif btype == "numbered_list_item":
            text = rich_text_plain(payload.get("rich_text"))
            out.append(indent + f"1. {text}")
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                out.extend(indent_lines(
                    _render_blocks(client, children, indent=""), indent + "   "
                ))

        elif btype == "to_do":
            text = rich_text_plain(payload.get("rich_text"))
            checked = payload.get("checked")
            box = "x" if checked else " "
            out.append(indent + f"- [{box}] {text}")
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                out.extend(indent_lines(_render_blocks(client, children, indent=""), indent + "  "))

        elif btype == "toggle":
            summary = rich_text_plain(payload.get("rich_text"))
            body: list[str] = []
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                body = _render_blocks(client, children, indent="")
            out.extend(indent_lines(render_toggle(summary, body), indent))
            out.append("")

        else:
            # MVP: preserve children even if we don't understand the block.
            # This is critical to avoid silent drops in nested structures.
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                out.extend(_render_blocks(client, children, indent=indent))

    return out
