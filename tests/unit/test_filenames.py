import pytest
from src.noteshift.filenames import generate_filename # Assuming this exists

def test_generate_filename_basic():
    # Test basic filename generation
    page_name = "My Awesome Note"
    expected_filename = "my-awesome-note.md"
    assert generate_filename(page_name) == expected_filename

def test_generate_filename_with_slashes():
    # Test filename generation with characters that should be sanitized
    page_name = "Note/With\\Slashes*&?"
    expected_filename = "note-with-slashes.md"
    assert generate_filename(page_name) == expected_filename

def test_generate_filename_empty():
    # Test generation with an empty page name
    page_name = ""
    expected_filename = ".md" # Or some default empty name handling
    assert generate_filename(page_name) == expected_filename

# Add more tests for edge cases, special characters, different title formats
