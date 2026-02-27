"""Tests for checkpoint module."""

from pathlib import Path

from noteshift.checkpoint import Checkpoint


def test_checkpoint_load_non_existent(tmp_path: Path) -> None:
    """Loading non-existent checkpoint returns empty checkpoint."""
    path = tmp_path / "checkpoints" / "nonexistent.json"
    cp = Checkpoint.load(path)
    assert isinstance(cp, Checkpoint)
    assert cp.page_ids == set()
    assert cp.database_ids == set()
    assert cp.files_written == []


def test_checkpoint_save_and_load(tmp_path: Path) -> None:
    """Checkpoint can be saved and reloaded."""
    path = tmp_path / "checkpoint.json"
    cp = Checkpoint()
    cp.add_page("page-123")
    cp.add_database("db-456")
    cp.add_file("test.md")
    cp.add_attachment()
    cp.add_rows(10)
    cp.add_warning("Test warning")

    cp.save(path)
    loaded = Checkpoint.load(path)

    assert loaded.page_ids == {"page-123"}
    assert loaded.database_ids == {"db-456"}
    assert loaded.files_written == ["test.md"]
    assert loaded.attachments_downloaded == 1
    assert loaded.rows_exported == 10
    assert loaded.warnings == ["Test warning"]
    assert loaded.timestamp != ""


def test_checkpoint_is_exported() -> None:
    """Check exported status."""
    cp = Checkpoint()
    cp.add_page("page-abc")
    cp.add_database("db-xyz")

    assert cp.is_page_exported("page-abc")
    assert cp.is_database_exported("db-xyz")
    assert not cp.is_page_exported("other-page")
    assert not cp.is_database_exported("other-db")


def test_checkpoint_get_stats() -> None:
    """Stats calculation."""
    cp = Checkpoint()
    cp.add_page("p1")
    cp.add_page("p2")
    cp.add_database("d1")
    cp.add_file("f1.md")
    cp.add_file("f2.md")
    cp.add_attachment()
    cp.add_rows(5)
    cp.add_warning("w1")

    stats = cp.get_stats()
    assert stats["pages_exported"] == 2
    assert stats["databases_exported"] == 1
    assert stats["files_written"] == 2
    assert stats["attachments_downloaded"] == 1
    assert stats["rows_exported"] == 5
    assert stats["warnings_count"] == 1


def test_checkpoint_dedupe_files() -> None:
    """Files are deduplicated."""
    cp = Checkpoint()
    cp.add_file("test.md")
    cp.add_file("test.md")  # duplicate
    assert cp.files_written == ["test.md"]
