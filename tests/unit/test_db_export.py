from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from noteshift.db_export import export_child_database


def test_export_child_database_success(tmp_path: Path) -> None:
    client = MagicMock()
    client.get_data_source.return_value = {
        "properties": {"Name": {"type": "title"}},
    }
    client.query_data_source.return_value = [{"id": "r1"}, {"id": "r2"}]

    result = export_child_database(
        client=client,
        data_source_id="db-1",
        title="Team Tasks",
        out_dir=tmp_path,
    )

    assert result.data_sources_exported == 1
    assert result.rows_exported == 2
    assert result.files_written == 3
    assert result.warnings == []


def test_export_child_database_handles_schema_error(tmp_path: Path) -> None:
    client = MagicMock()
    client.get_data_source.side_effect = RuntimeError("schema boom")
    client.query_data_source.return_value = [{"id": "r1"}]

    result = export_child_database(
        client=client,
        data_source_id="db-1",
        title="Team Tasks",
        out_dir=tmp_path,
    )

    assert result.rows_exported == 1
    assert result.files_written == 2
    assert any("Failed to fetch schema" in warning for warning in result.warnings)


def test_export_child_database_handles_query_error(tmp_path: Path) -> None:
    client = MagicMock()
    client.get_data_source.return_value = {"properties": {}}
    client.query_data_source.side_effect = RuntimeError("query boom")

    result = export_child_database(
        client=client,
        data_source_id="db-1",
        title="Team Tasks",
        out_dir=tmp_path,
    )

    assert result.rows_exported == 0
    assert result.files_written == 2
    assert any("Failed to query data source" in warning for warning in result.warnings)
