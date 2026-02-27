import pytest
from src.noteshift.checkpoint import load_checkpoint, save_checkpoint # Assuming these exist

def test_load_checkpoint_non_existent(tmp_path):
    # Test loading a checkpoint from a non-existent file
    file_path = tmp_path / "non_existent_checkpoint.json"
    checkpoint_data = load_checkpoint(file_path)
    assert checkpoint_data is None # Or expect a specific default

def test_save_and_load_checkpoint(tmp_path):
    # Test saving and then loading a checkpoint
    file_path = tmp_path / "test_checkpoint.json"
    data_to_save = {"last_processed_page": "page123", "timestamp": "2023-01-01T10:00:00Z"}
    save_checkpoint(file_path, data_to_save)
    loaded_data = load_checkpoint(file_path)
    assert loaded_data == data_to_save

# Add more tests for different scenarios, e.g., invalid JSON, empty data
