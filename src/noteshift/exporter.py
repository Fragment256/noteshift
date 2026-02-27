from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from noteshift.checkpoint import Checkpoint
from noteshift.db_export import export_child_database
from noteshift.filenames import FilenamePolicy, NameDeduper
from noteshift.license import check_depth_limit, get_depth_warning, verify_license
from noteshift.markdown import indent_lines, render_toggle, rich_text_plain, rich_text_to_markdown
from noteshift.notion import NotionClient


@dataclass
class ExportResult:
    pages_exported: int = 0
    files_written: int = 0
    warnings: list[str] = field(default_factory=list)
    databases_exported: int = 0
    rows_exported: int = 0
    attachments_downloaded: int = 0


def _page_title(page: dict) -> str:
    props = page.get("properties", {})
    # Title property can be named anything; find the first with type 'title'
    for v in props.values():
        if isinstance(v, dict) and v.get("type") == "title":
            return rich_text_plain(v.get("title"))
    return "Untitled"


def _get_attachment_info(block: dict) -> tuple[str | None, str | None, str | None]:
    """Extracts URL, caption, and type from attachment blocks."""
    btype = block.get("type")
    payload = block.get(btype, {}) if btype else {}

    if btype == "image":
        url = payload.get("file", {}).get("url")
        caption = rich_text_to_markdown(payload.get("caption"), page_map={})  # No internal links in captions
        return url, caption, "image"
    elif btype == "file":
        url = payload.get("file", {}).get("url")
        caption = rich_text_to_markdown(payload.get("caption"), page_map={})  # No internal links in captions
        return url, caption, "file"
    return None, None, None


def export_page_tree(
    *,
    token: str,
    root_page_id: str,
    out_dir: Path,
    checkpoint: Checkpoint | None = None,
    force: bool = False,
    license_key: str | None = None,
    max_depth: int = 2,
) -> ExportResult:
    """Export a page and its subpages.

    MVP scope for recursion:
    - Follow `child_page` blocks.
    - Create subfolders mirroring the page tree.
    - Rewrite internal links.
    - Download attachments and relink them.
    """

    client = NotionClient(token)
    policy = FilenamePolicy()
    # Stores {page_id: relative_md_path} without extension for Obsidian compatibility
    page_map: dict[str, str] = {}

    result = ExportResult()

    # License verification
    license_info = verify_license(license_key)
    effective_max_depth = license_info["max_depth"] if license_key else max_depth
    has_license = license_key is not None

    visited: set[str] = set()
    depth_limited_ids: set[str] = set()

    def export_one(page_id: str, parent_dir: Path, depth: int = 0) -> None:
        nonlocal result
        if page_id in visited:
            return
        visited.add(page_id)

        # Skip if already exported (unless force mode)
        if not force and checkpoint.is_page_exported(page_id):
            return

        page = client.get_page(page_id)
        title = _page_title(page)

        deduper = NameDeduper()
        stem = deduper.dedupe(policy.slug(title))

        page_dir = parent_dir / stem
        page_dir.mkdir(parents=True, exist_ok=True)

        # Define the output markdown path and create the assets directory
        md_path = page_dir / "index.md"
        assets_dir = page_dir / "_assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        # Store the relative path for link mapping
        page_map[page_id] = md_path.relative_to(out_dir).with_suffix("").as_posix()

        lines: list[str] = [f"# {title}", ""]
        blocks = client.list_block_children(page_id)

        # Process blocks: render content, download attachments
        rendered_content_lines: list[str] = []
        for b in blocks:
            btype = b.get("type")

            if btype == "child_database":
                ds_id = b.get("id")
                if not ds_id:
                    result.warnings.append(f"child_database missing id on page {page_id}")
                    continue

                # Skip if already exported (unless force mode)
                if not force and checkpoint.is_database_exported(ds_id):
                    continue

                title_db = (b.get("child_database") or {}).get("title") or "Database"
                res = export_child_database(
                    client=client,
                    data_source_id=ds_id,
                    title=title_db,
                    out_dir=page_dir,
                )
                result.warnings.extend(res.warnings)
                result.files_written += res.files_written
                result.databases_exported += res.data_sources_exported
                result.rows_exported += res.rows_exported
                result.attachments_downloaded += res.attachments_downloaded

                # Update checkpoint
                checkpoint.add_database(ds_id)
                checkpoint.add_rows(res.rows_exported)
                for w in res.warnings:
                    checkpoint.add_warning(w)
                result._exported_database_ids.append(ds_id)

            elif btype in {"image", "file"}:
                url, caption, _ = _get_attachment_info(b)
                if url:
                    try:
                        filename = Path(url.split("/")[-1].split("?")[0])  # Basic extraction
                        # Sanitize filename and ensure it's unique within _assets
                        sanitized_filename = Path(policy.slug(str(filename)))
                        deduped_filename = deduper.dedupe(str(sanitized_filename))
                        file_path = assets_dir / deduped_filename

                        client.download_file(url, file_path)

                        # Format markdown reference
                        # Use relative path from md_path to the asset
                        asset_md_ref = Path("_assets") / deduped_filename
                        asset_md_ref_str = asset_md_ref.as_posix()

                        if caption:
                            rendered_content_lines.append(f"![{caption}]({asset_md_ref_str})")
                        else:
                            rendered_content_lines.append(f"![{deduped_filename}]({asset_md_ref_str})")

                        result.attachments_downloaded += 1

                    except Exception as e:  # noqa: BLE001
                        result.warnings.append(f"Failed to download attachment {url} for page {title}: {e}")
                else:
                    result.warnings.append(f"Attachment block missing URL or type on page {title}")

            else:
                # For other block types, treat them as content to be rendered
                # These will be processed by _render_blocks later
                pass

        # Append blocks that weren't attachments
        lines.extend(_render_blocks(client, blocks, indent="", page_map=page_map))

        # Add downloaded attachments to the content
        lines.extend(rendered_content_lines)

        md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

        result.pages_exported += 1
        result.files_written += 1  # Count the markdown file itself

        # Update checkpoint
        checkpoint.add_page(page_id)
        checkpoint.add_file(str(md_path.relative_to(out_dir)))

        # recurse into child pages (with depth limit check)
        if not check_depth_limit(depth, effective_max_depth, has_license):
            warning = get_depth_warning(depth, effective_max_depth)
            if warning and page_id not in depth_limited_ids:
                result.warnings.append(warning)
                depth_limited_ids.add(page_id)
            return

        for b in blocks:
            if b.get("type") == "child_page":
                child_id = b.get("id")
                if child_id:
                    export_one(child_id, page_dir, depth + 1)

    export_one(root_page_id, out_dir)
    return result


def _render_blocks(
    client: NotionClient,
    blocks: list[dict],
    indent: str,
    page_map: dict[str, str],  # Pass page_map to render_blocks
) -> list[str]:
    """Renders blocks that are not attachments or child_databases."""
    out: list[str] = []

    for b in blocks:
        btype = b.get("type")
        payload = b.get(btype, {}) if btype else {}

        if btype in {"image", "file", "child_database", "child_page"}:
            # Skip block types handled elsewhere or recursively
            continue

        if btype == "paragraph":
            text = rich_text_to_markdown(payload.get("rich_text"), page_map)
            if text:
                out.append(indent + text)
                out.append("")

        elif btype in {"heading_1", "heading_2", "heading_3"}:
            level = {"heading_1": "#", "heading_2": "##", "heading_3": "###"}[btype]
            text = rich_text_to_markdown(payload.get("rich_text"), page_map)
            out.append(indent + f"{level} {text}")
            out.append("")

        elif btype == "bulleted_list_item":
            text = rich_text_to_markdown(payload.get("rich_text"), page_map)
            out.append(indent + f"- {text}")
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                out.extend(
                    indent_lines(
                        _render_blocks(
                            client, children, indent="", page_map=page_map
                        ),
                        indent + "  ",
                    )
                )

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
                out.extend(
                    indent_lines(
                        _render_blocks(
                            client, children, indent="", page_map=page_map
                        ),
                        indent + "  ",
                    )
                )

        elif btype == "toggle":
            summary = rich_text_to_markdown(payload.get("rich_text"), page_map)
            body: list[str] = []
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                body = _render_blocks(client, children, indent="", page_map=page_map)
            out.extend(indent_lines(render_toggle(summary, body), indent))
            out.append("")

        else:
            # For unhandled block types, preserve children if they exist
            if b.get("has_children"):
                children = client.list_block_children(b["id"])
                out.extend(_render_blocks(client, children, indent=indent, page_map=page_map))

    return out
