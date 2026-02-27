"""Tests for markdown conversion utilities."""

import pytest
from noteshift.markdown import (
    rich_text_to_markdown,
    rich_text_plain,
    md_escape,
    render_toggle,
)

# Mock data structures that mimic Notion API responses
NOTION_RICH_TEXT_PLAIN = [
    {"type": "text", "text": {"content": "Hello, "}},
    {"type": "text", "text": {"content": "world!"}},
]

NOTION_RICH_TEXT_BOLD = [
    {"type": "text", "text": {"content": "This is "}},
    {"type": "text", "annotations": {"bold": True}, "text": {"content": "bold"}},
    {"type": "text", "text": {"content": " text."}},
]

NOTION_RICH_TEXT_ITALIC = [
    {"type": "text", "text": {"content": "This is "}},
    {"type": "text", "annotations": {"italic": True}, "text": {"content": "italic"}},
    {"type": "text", "text": {"content": " text."}},
]

NOTION_RICH_TEXT_CODE = [
    {"type": "text", "annotations": {"code": True}, "text": {"content": "print('hello')"}},
]

NOTION_RICH_TEXT_LINK = [
    {"type": "text", "text": {"content": "Visit "}},
    {
        "type": "text",
        "text": {
            "content": "Google",
            "link": {"url": "https://www.google.com"},
        },
    },
]

NOTION_RICH_TEXT_USER_MENTION = [
    {"type": "mention", "mention": {"type": "user", "user": {"id": "user-456"}}, "plain_text": "John Doe"}
]

NOTION_RICH_TEXT_DATE_MENTION = [
    {"type": "mention", "mention": {"type": "date", "date": {"start": "2023-10-27"}}, "plain_text": "2023-10-27"}
]


def test_rich_text_plain_basic():
    """Test extracting plain text from basic rich text."""
    assert rich_text_plain(NOTION_RICH_TEXT_PLAIN) == "Hello, world!"


def test_rich_text_plain_with_annotations():
    """Test extracting plain text when annotations are present."""
    assert rich_text_plain(NOTION_RICH_TEXT_BOLD) == "This is bold text."


def test_rich_text_to_markdown_basic():
    """Test basic rich text to markdown conversion."""
    assert rich_text_to_markdown(NOTION_RICH_TEXT_PLAIN) == "Hello, world!"


def test_rich_text_to_markdown_bold():
    """Test bold annotation."""
    expected = "This is **bold** text."
    assert rich_text_to_markdown(NOTION_RICH_TEXT_BOLD) == expected


def test_rich_text_to_markdown_italic():
    """Test italic annotation."""
    expected = "This is *italic* text."
    assert rich_text_to_markdown(NOTION_RICH_TEXT_ITALIC) == expected


def test_rich_text_to_markdown_code():
    """Test code annotation."""
    expected = "`print('hello')`"
    assert rich_text_to_markdown(NOTION_RICH_TEXT_CODE) == expected


def test_rich_text_to_markdown_link():
    """Test URL link conversion."""
    expected = "Visit [Google](https://www.google.com)"
    assert rich_text_to_markdown(NOTION_RICH_TEXT_LINK) == expected


def test_rich_text_to_markdown_user_mention():
    """Test user mention conversion."""
    expected = "John Doe"
    assert rich_text_to_markdown(NOTION_RICH_TEXT_USER_MENTION) == expected


def test_rich_text_to_markdown_date_mention():
    """Test date mention conversion."""
    expected = "2023-10-27"
    assert rich_text_to_markdown(NOTION_RICH_TEXT_DATE_MENTION) == expected


def test_rich_text_to_markdown_url_pipe_escape():
    """Test escaping pipe characters in link text."""
    rt_with_pipe = [{
        "type": "text",
        "text": {
            "content": "Link | With | Pipe",
            "link": {"url": "https://example.com"}
        }
    }]
    expected = "[Link \\| With \\| Pipe](https://example.com)"
    assert rich_text_to_markdown(rt_with_pipe) == expected


def test_md_escape():
    """Test markdown escaping."""
    assert md_escape("Hello\r\nWorld") == "Hello\nWorld"
    assert md_escape("Hello\rWorld") == "Hello\nWorld"
    assert md_escape("Hello\nWorld") == "Hello\nWorld"


def test_render_toggle():
    """Test rendering of toggle blocks."""
    summary = "Toggle Summary"
    body_lines = ["Line 1", "Line 2"]
    expected = [
        "<details><summary>Toggle Summary</summary>",
        "",
        "Line 1",
        "Line 2",
        "",
        "</details>"
    ]
    assert render_toggle(summary, body_lines) == expected

