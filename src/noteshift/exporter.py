from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from noteshift.db_export import export_child_database
from noteshift.filenames import FilenamePolicy, NameDeduper
from noteshift.markdown import indent_lines, md_escape, render_toggle, rich_text_plain, rich_text_to_markdown
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
    """Export a page and its subpages.

    MVP scope for recursion:
    - Follow `child_page` blocks.
    - Create subfolders mirroring the page tree.

    Not yet:
    - Link rewriting across notes
    - Attachments
    """

    client = NotionClient(token)
    policy = FilenamePolicy()
    page_map: dict[str, str] = {}  # Stores {page_id: relative_md_path}

    pages_exported = 0
    files_written = 0
    warnings: list[str] = []

    visited: set[str] = set()

    def export_one(page_id: str, parent_dir: Path) -> None:
        nonlocal pages_exported, files_written
        if page_id in visited:
            return
        visited.add(page_id)

        page = client.get_page(page_id)
        title = _page_title(page)

        deduper = NameDeduper()
        stem = deduper.dedupe(policy.slug(title))

        page_dir = parent_dir / stem
        page_dir.mkdir(parents=True, exist_ok=True)
        md_path = page_dir / "index.md"
        # Store the relative path for link mapping
        page_map[page_id] = md_path.relative_to(out_dir).with_suffix("").as_posix()

        lines: list[str] = [f"# {title}", ""]
        blocks = client.list_block_children(page_id)
        # export any child databases found on this page
        for b in blocks:
            if b.get("type") == "child_database":
                title_db = (b.get("child_database") or {}).get("title") or "Database"
                ds_id = b.get("id")
                if not ds_id:
                    warnings.append(f"child_database missing id on page {page_id}")
                    continue
                res = export_child_database(
                    client=client,
                    data_source_id=ds_id,
                    title=title_db,
                    out_dir=page_dir,
                )
                warnings.extend(res.warnings)
                files_written += res.files_written
        
        # Use the updated rich_text_to_markdown renderer
        rendered_blocks = _render_blocks(client, blocks, indent="", page_map=page_map)
        lines.extend(rendered_blocks)

        md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

        pages_exported += 1
        files_written += 1

        # recurse into child pages
        for b in blocks:
            if b.get("type") == "child_page":
                child_id = b.get("id")
                if child_id:
                    export_one(child_id, page_dir)

    export_one(root_page_id, out_dir)
    return ExportResult(
        pages_exported=pages_exported, files_written=files_written, warnings=warnings
    )


def _render_blocks(
    client: NotionClient,
    blocks: list[dict],
    indent: str,
    page_map: dict[str, str],  # Pass page_map to render_blocks
) -> list[str]:
    out: list[str] = []

    for b in blocks:
        btype = b.get("type")
        payload = b.get(btype, {}) if btype else {}

        if btype == "paragraph":
            # Use rich_text_to_markdown for paragraphs
            text = rich_text_to_markdown(payload.get("rich_text"), page_map)
            if text:
                out.append(indent + text)
                out.append("")

        elif btype in {"heading_1", "heading_2", "heading_3"}:
            level = {"heading_1": "#", "heading_2": "##", "heading_3": "###"}[btype]
            # Use rich_text_to_markdown for headings
            text = rich_text_to_markdown(payload.get("rich_text"), page_map)
            out.append(indent + f"{level} {text}")
            out.append("")

        elif btype == "bulleted_list_item":
            text = rich_text_to_markdown(payload.get("rich_text"), page_map)
            out.append(indent + f"- {text}")
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                out.extend(indent_lines(_render_blocks(client, children, indent="", page_map=page_map), indent + "  "))

        elif btype == "numbered_list_item":
            text = rich_text_to_markdown(payload.get("rich_text"), page_map)
            out.append(indent + f"1. {text}")
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                out.extend(indent_lines(
                    _render_blocks(client, children, indent="", page_map=page_map), indent + "   "
                ))

        elif btype == "to_do":
            text = rich_text_to_markdown(payload.get("rich_text"), page_map)
            checked = payload.get("checked")
            box = "x" if checked else " "
            out.append(indent + f"- [{box}] {text}")
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                out.extend(indent_lines(_render_blocks(client, children, indent="", page_map=page_map), indent + "  "))

        elif btype == "toggle":
            summary = rich_text_to_markdown(payload.get("rich_text"), page_map)
            body: list[str] = []
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                body = _render_blocks(client, children, indent="", page_map=page_map)
            out.extend(indent_lines(render_toggle(summary, body), indent))
            out.append("")

        else:
            # MVP: preserve children even if we don't understand the block.
            # This is critical to avoid silent drops in nested structures.
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                out.extend(_render_blocks(client, children, indent=indent, page_map=page_map))

    return out
