"""Tests for filename generation."""

from noteshift.filenames import FilenamePolicy, NameDeduper
import pytest


def test_filename_policy_slug() -> None:
    """Test slugification of titles."""
    policy = FilenamePolicy()
    assert policy.slug("My Awesome Note Title") == "My-Awesome-Note-Title"
    assert policy.slug("Note/With\\Slashes*&?") == "Note-With-Slashes"
    assert policy.slug("  Leading/Trailing Spaces  ") == "Leading-Trailing-Spaces"
    assert policy.slug("Special Chars: !@#$%^&()") == "Special-Chars"
    assert policy.slug("Already-Kebab-Case") == "Already-Kebab-Case"
    assert policy.slug("") == "untitled"
    assert policy.slug(" ") == "untitled"
    assert policy.slug("A" * 120) == "A" * 100  # Test max_len


def test_filename_policy_windows_safe() -> None:
    """Test Windows-specific filename sanitization."""
    policy = FilenamePolicy()
    # Test invalid characters are replaced/removed
    test_str_with_invalid = "File<>:\"/\\|?*\\x00\\x1fchars."
    sanitized = policy.slug(test_str_with_invalid)
    
    # Check that invalid characters are not present
    assert "<" not in sanitized
    assert ">" not in sanitized
    assert ":" not in sanitized
    assert '"' not in sanitized
    assert "/" not in sanitized
    assert "\\" not in sanitized
    assert "|" not in sanitized
    assert "?" not in sanitized
    assert "*" not in sanitized

    # Test trailing dots and spaces are removed
    assert policy.slug("FileWithTrailing.") == "FileWithTrailing"
    assert policy.slug("FileWithTrailing ") == "FileWithTrailing"
    assert policy.slug("FileWithTrailing. ") == "FileWithTrailing"


def test_name_deduper() -> None:
    """Test deduplication of filenames."""
    deduper = NameDeduper()

    # First call returns stem
    assert deduper.dedupe("base") == "base"
    # Second call returns stem-2
    assert deduper.dedupe("base") == "base-2"
    # Different stem starts fresh
    assert deduper.dedupe("another") == "another"
    # Third call for "base" returns stem-3
    assert deduper.dedupe("base") == "base-3"
    # Second call for "another" returns stem-2
    assert deduper.dedupe("another") == "another-2"

    # Test with different stems that might collide if not careful
    # "file" was never called before, so starts fresh
    assert deduper.dedupe("file") == "file"
    # "file-2" is a different stem, starts fresh
    assert deduper.dedupe("file-2") == "file-2"
    # "file" was seen once before, so now becomes 2
    assert deduper.dedupe("file") == "file-2"
