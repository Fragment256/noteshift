"""Tests for exporter module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from noteshift.exporter import ExportResult, export_page_tree


class TestExportPageTree:
    """Tests for export_page_tree function."""

    @pytest.fixture
    def mock_notion_client(self):
        """Mock NotionClient with basic page structure."""
        with patch("noteshift.exporter.NotionClient") as mock:
            client = MagicMock()

            # Mock get_page to return a page with title
            def get_page(page_id: str) -> dict:
                return {
                    "id": page_id,
                    "properties": {
                        "title": {"title": [{"text": {"content": f"Page {page_id}"}}]}
                    },
                }

            client.get_page = get_page

            # Mock list_block_children to return no children
            client.list_block_children.return_value = []

            mock.return_value = client
            yield client

    @pytest.fixture
    def minimal_checkpoint(self, tmp_path: Path):
        """Load a minimal checkpoint."""
        from noteshift.checkpoint import Checkpoint

        return Checkpoint.load(tmp_path / ".checkpoint.json")

    def test_export_single_page(
        self, tmp_path: Path, mock_notion_client, minimal_checkpoint
    ) -> None:
        """Export a single page with no children."""
        out_dir = tmp_path / "export"

        result = export_page_tree(
            token="test-token",
            root_page_id="root-page",
            out_dir=out_dir,
            checkpoint=minimal_checkpoint,
        )

        assert result.pages_exported == 1
        assert result.files_written == 1
        assert len(result.warnings) == 0

        # Just check a directory was created (slug name varies)
        assert any(out_dir.iterdir())

    def test_export_with_child_page(
        self, tmp_path: Path, mock_notion_client, minimal_checkpoint
    ) -> None:
        """Export page with one child."""

        # Set up child page block
        def get_page(page_id: str) -> dict:
            titles = {
                "root-page": "Root Page",
                "child-page": "Child Page",
            }
            return {
                "id": page_id,
                "properties": {
                    "title": {
                        "title": [
                            {
                                "text": {
                                    "content": titles.get(page_id, f"Page {page_id}")
                                }
                            }
                        ]
                    }
                },
            }

        mock_notion_client.get_page = get_page

        # First call returns root with child, second call returns no children
        call_count = [0]

        def list_children(page_id: str) -> list:
            call_count[0] += 1
            if call_count[0] == 1:
                return [{"id": "child-page", "type": "child_page"}]
            return []

        mock_notion_client.list_block_children = list_children

        out_dir = tmp_path / "export"

        result = export_page_tree(
            token="test-token",
            root_page_id="root-page",
            out_dir=out_dir,
            checkpoint=minimal_checkpoint,
        )

        assert result.pages_exported == 2  # root + child

    def test_depth_limit_free_tier(
        self, tmp_path: Path, mock_notion_client, minimal_checkpoint
    ) -> None:
        """Free tier stops at depth=2 with warning."""
        pages = {}
        page_counter = [0]

        def get_page(page_id: str) -> dict:
            page_counter[0] += 1
            pages[page_id] = f"Page {page_counter[0]}"
            return {
                "id": page_id,
                "properties": {
                    "title": {"title": [{"text": {"content": pages[page_id]}}]}
                },
            }

        mock_notion_client.get_page = get_page

        def list_children(page_id: str) -> list:
            depth = {"root": 0, "child": 1, "grandchild": 2}
            current_depth = depth.get(page_id, 3)
            if current_depth < 3:
                next_id = ["child", "grandchild", "great-grandchild"][current_depth]
                return [{"id": next_id, "type": "child_page"}]
            return []

        mock_notion_client.list_block_children = list_children

        out_dir = tmp_path / "export"

        result = export_page_tree(
            token="test-token",
            root_page_id="root",
            out_dir=out_dir,
            checkpoint=minimal_checkpoint,
            max_depth=2,
        )

        assert result.pages_exported == 3
        assert any("Depth limit" in w for w in result.warnings)

    def test_depth_limit_high_max_depth(
        self, tmp_path: Path, mock_notion_client, minimal_checkpoint
    ) -> None:
        """High max_depth exports deeper trees."""
        pages = {}
        page_counter = [0]

        def get_page(page_id: str) -> dict:
            page_counter[0] += 1
            pages[page_id] = f"Page {page_counter[0]}"
            return {
                "id": page_id,
                "properties": {
                    "title": {"title": [{"text": {"content": pages[page_id]}}]}
                },
            }

        mock_notion_client.get_page = get_page

        # Create a deep chain
        def list_children(page_id: str) -> list:
            depth_map = {"root": 0, "child": 1, "grandchild": 2, "great-grandchild": 3}
            current_depth = depth_map.get(page_id, 4)
            if current_depth < 4:
                next_ids = [
                    "child",
                    "grandchild",
                    "great-grandchild",
                    "great-great-grandchild",
                ]
                return [{"id": next_ids[current_depth], "type": "child_page"}]
            return []

        mock_notion_client.list_block_children = list_children

        out_dir = tmp_path / "export"

        result = export_page_tree(
            token="test-token",
            root_page_id="root",
            out_dir=out_dir,
            checkpoint=minimal_checkpoint,
            max_depth=10,
        )

        # Should export all 5 pages with sufficiently high depth
        assert result.pages_exported == 5
        assert not any("Depth limit" in w for w in result.warnings)

    def test_force_mode_skips_checkpoint(
        self, tmp_path: Path, mock_notion_client
    ) -> None:
        """Force mode re-exports already exported pages."""
        from noteshift.checkpoint import Checkpoint

        checkpoint = Checkpoint()
        checkpoint.add_page("root-page")

        out_dir = tmp_path / "export"

        # Without force, root-page would be skipped
        result = export_page_tree(
            token="test-token",
            root_page_id="root-page",
            out_dir=out_dir,
            checkpoint=checkpoint,
            force=True,
        )

        assert result.pages_exported == 1  # Re-exported due to force


class TestExportResult:
    """Tests for ExportResult dataclass."""

    def test_export_result_defaults(self) -> None:
        """ExportResult has sensible defaults."""
        result = ExportResult()
        assert result.pages_exported == 0
        assert result.files_written == 0
        assert result.databases_exported == 0
        assert result.rows_exported == 0
        assert result.attachments_downloaded == 0
        assert result.warnings == []

    def test_export_result_accumulation(self) -> None:
        """ExportResult fields can be accumulated."""
        result = ExportResult()
        result.pages_exported += 5
        result.files_written += 5
        result.warnings.append("Test warning")

        assert result.pages_exported == 5
        assert result.files_written == 5
        assert result.warnings == ["Test warning"]
