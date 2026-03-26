from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from noteshift.exporter import export_page_tree


def test_child_database_id_is_resolved(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """child_database blocks often expose a database_id; exporter should resolve it."""

    # Patch NotionClient constructor used by export_page_tree
    with patch("noteshift.exporter.NotionClient") as mock_client:
        client = MagicMock()

        client.get_page.return_value = {
            "id": "root",
            "properties": {"title": {"title": [{"text": {"content": "Root"}}]}},
        }

        # Root has a child_database block with id "db-raw"
        client.list_block_children.return_value = [
            {
                "id": "db-raw",
                "type": "child_database",
                "child_database": {"title": "DB"},
            },
        ]

        client.resolve_data_source_id.return_value = "ds-1"

        mock_client.return_value = client

        called: dict[str, str] = {}

        def fake_export_child_database(
            *, client, data_source_id: str, title: str, out_dir
        ):
            _ = client
            _ = out_dir
            called["data_source_id"] = data_source_id
            called["title"] = title

            class _Res:
                warnings: list[str] = []
                files_written: int = 0
                data_sources_exported: int = 1
                rows_exported: int = 0
                attachments_downloaded: int = 0

            return _Res()

        monkeypatch.setattr(
            "noteshift.exporter.export_child_database", fake_export_child_database
        )

        from noteshift.checkpoint import Checkpoint

        checkpoint = Checkpoint()
        out_dir = tmp_path / "out"

        res = export_page_tree(
            token="t",
            root_page_id="root",
            out_dir=out_dir,
            checkpoint=checkpoint,
            force=True,
            max_depth=0,
        )

        assert res.databases_exported == 1
        assert called["data_source_id"] == "ds-1"
        assert called["title"] == "DB"
