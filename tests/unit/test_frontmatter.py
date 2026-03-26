"""Tests for frontmatter generation."""

import pytest

from noteshift.frontmatter import build_frontmatter


# ---------------------------------------------------------------------------
# Fixture page dicts (mimic Notion API page objects)
# ---------------------------------------------------------------------------

STANDALONE_PAGE = {
    "id": "abc12345-0000-0000-0000-000000000000",
    "url": "https://www.notion.so/My-Page-abc1234500000000000000000000",
    "created_time": "2024-01-01T10:00:00.000Z",
    "last_edited_time": "2024-06-15T14:30:00.000Z",
    "properties": {
        "title": {
            "type": "title",
            "title": [{"plain_text": "My Page"}],
        }
    },
}

PAGE_MISSING_OPTIONAL_FIELDS = {
    "id": "def56789-0000-0000-0000-000000000000",
    # no "url", no "created_time", no "last_edited_time"
    "properties": {
        "title": {
            "type": "title",
            "title": [{"plain_text": "Incomplete Page"}],
        }
    },
}

DATABASE_PAGE = {
    "id": "db000001-0000-0000-0000-000000000000",
    "url": "https://www.notion.so/Task-db00000100000000000000000000",
    "created_time": "2025-03-01T09:00:00.000Z",
    "last_edited_time": "2025-03-20T17:00:00.000Z",
    "properties": {
        "Name": {
            "type": "title",
            "title": [{"plain_text": "My Task"}],
        },
        "Status": {
            "type": "select",
            "select": {"name": "Done"},
        },
        "Priority": {
            "type": "number",
            "number": 3,
        },
        "Published": {
            "type": "checkbox",
            "checkbox": True,
        },
        "Tags": {
            "type": "multi_select",
            "multi_select": [{"name": "python"}, {"name": "tutorial"}],
        },
        "Due Date": {
            "type": "date",
            "date": {"start": "2025-04-01"},
        },
        "Website": {
            "type": "url",
            "url": "https://example.com",
        },
        "Contact Email": {
            "type": "email",
            "email": "hello@example.com",
        },
        "Phone": {
            "type": "phone_number",
            "phone_number": "+1-555-1234",
        },
        "Notes": {
            "type": "rich_text",
            "rich_text": [{"plain_text": "Some notes here"}],
        },
    },
}

PAGE_EMPTY_PROPERTIES = {
    "id": "ee000001-0000-0000-0000-000000000000",
    "url": "https://www.notion.so/Empty-ee00000100000000000000000000",
    "created_time": "2025-01-01T00:00:00.000Z",
    "last_edited_time": "2025-01-01T00:00:00.000Z",
    "properties": {
        "Title": {
            "type": "title",
            "title": [{"plain_text": "Empty Props Page"}],
        },
        "Status": {
            "type": "select",
            "select": None,  # empty select
        },
        "Tags": {
            "type": "multi_select",
            "multi_select": [],  # empty multi-select
        },
        "Due Date": {
            "type": "date",
            "date": None,  # empty date
        },
        "Notes": {
            "type": "rich_text",
            "rich_text": [],  # empty rich text
        },
    },
}

PAGE_UNSUPPORTED_PROPERTIES = {
    "id": "ff000001-0000-0000-0000-000000000000",
    "url": "https://www.notion.so/Unsupported-ff00000100000000000000000000",
    "created_time": "2025-01-01T00:00:00.000Z",
    "last_edited_time": "2025-01-01T00:00:00.000Z",
    "properties": {
        "Name": {
            "type": "title",
            "title": [{"plain_text": "Unsupported Page"}],
        },
        "Assignee": {
            "type": "people",
            "people": [{"name": "Alice"}],
        },
        "Linked Pages": {
            "type": "relation",
            "relation": [{"id": "some-id"}],
        },
        "Formula Result": {
            "type": "formula",
            "formula": {"type": "number", "number": 42},
        },
    },
}


# ---------------------------------------------------------------------------
# Tests: core fields
# ---------------------------------------------------------------------------


class TestBuildFrontmatterCoreFields:
    def test_returns_string_with_delimiters(self) -> None:
        result = build_frontmatter(STANDALONE_PAGE)
        assert result.startswith("---\n")
        assert result.endswith("---\n")

    def test_contains_notion_id(self) -> None:
        result = build_frontmatter(STANDALONE_PAGE)
        assert "abc12345-0000-0000-0000-000000000000" in result

    def test_contains_notion_url(self) -> None:
        result = build_frontmatter(STANDALONE_PAGE)
        assert "notion.so" in result

    def test_contains_created_at(self) -> None:
        result = build_frontmatter(STANDALONE_PAGE)
        assert "2024-01-01T10:00:00.000Z" in result

    def test_contains_updated_at(self) -> None:
        result = build_frontmatter(STANDALONE_PAGE)
        assert "2024-06-15T14:30:00.000Z" in result

    def test_contains_title(self) -> None:
        result = build_frontmatter(STANDALONE_PAGE)
        assert "My Page" in result

    def test_valid_yaml(self) -> None:
        import yaml

        result = build_frontmatter(STANDALONE_PAGE)
        inner = result.strip().lstrip("---").rstrip("---").strip()
        parsed = yaml.safe_load(inner)
        assert isinstance(parsed, dict)
        assert parsed["notionId"] == "abc12345-0000-0000-0000-000000000000"
        assert parsed["title"] == "My Page"

    def test_key_names(self) -> None:
        import yaml

        result = build_frontmatter(STANDALONE_PAGE)
        inner = result.strip().lstrip("---").rstrip("---").strip()
        parsed = yaml.safe_load(inner)
        assert "notionId" in parsed
        assert "notionUrl" in parsed
        assert "createdAt" in parsed
        assert "updatedAt" in parsed
        assert "title" in parsed


# ---------------------------------------------------------------------------
# Tests: missing optional fields
# ---------------------------------------------------------------------------


class TestBuildFrontmatterMissingFields:
    def test_missing_url_produces_null(self) -> None:
        import yaml

        result = build_frontmatter(PAGE_MISSING_OPTIONAL_FIELDS)
        inner = result.strip().lstrip("---").rstrip("---").strip()
        parsed = yaml.safe_load(inner)
        assert parsed["notionUrl"] is None

    def test_missing_timestamps_produce_null(self) -> None:
        import yaml

        result = build_frontmatter(PAGE_MISSING_OPTIONAL_FIELDS)
        inner = result.strip().lstrip("---").rstrip("---").strip()
        parsed = yaml.safe_load(inner)
        assert parsed["createdAt"] is None
        assert parsed["updatedAt"] is None

    def test_still_has_all_core_keys(self) -> None:
        import yaml

        result = build_frontmatter(PAGE_MISSING_OPTIONAL_FIELDS)
        inner = result.strip().lstrip("---").rstrip("---").strip()
        parsed = yaml.safe_load(inner)
        for key in ("notionId", "notionUrl", "createdAt", "updatedAt", "title"):
            assert key in parsed


# ---------------------------------------------------------------------------
# Tests: database properties
# ---------------------------------------------------------------------------


class TestBuildFrontmatterDatabaseProperties:
    def _parsed(self, page: dict) -> dict:
        import yaml

        result = build_frontmatter(page)
        inner = result.strip().lstrip("---").rstrip("---").strip()
        return yaml.safe_load(inner)

    def test_select_property(self) -> None:
        parsed = self._parsed(DATABASE_PAGE)
        assert parsed["status"] == "Done"

    def test_number_property(self) -> None:
        parsed = self._parsed(DATABASE_PAGE)
        assert parsed["priority"] == 3

    def test_checkbox_property(self) -> None:
        parsed = self._parsed(DATABASE_PAGE)
        assert parsed["published"] is True

    def test_multi_select_property(self) -> None:
        parsed = self._parsed(DATABASE_PAGE)
        assert parsed["tags"] == ["python", "tutorial"]

    def test_date_property(self) -> None:
        parsed = self._parsed(DATABASE_PAGE)
        assert parsed["due_date"] == "2025-04-01"

    def test_url_property(self) -> None:
        parsed = self._parsed(DATABASE_PAGE)
        assert parsed["website"] == "https://example.com"

    def test_email_property(self) -> None:
        parsed = self._parsed(DATABASE_PAGE)
        assert parsed["contact_email"] == "hello@example.com"

    def test_phone_property(self) -> None:
        parsed = self._parsed(DATABASE_PAGE)
        assert parsed["phone"] == "+1-555-1234"

    def test_rich_text_property(self) -> None:
        parsed = self._parsed(DATABASE_PAGE)
        assert parsed["notes"] == "Some notes here"

    def test_property_key_slugified(self) -> None:
        # "Due Date" -> "due_date", "Contact Email" -> "contact_email"
        parsed = self._parsed(DATABASE_PAGE)
        assert "due_date" in parsed
        assert "contact_email" in parsed

    def test_title_property_not_duplicated(self) -> None:
        # The title property is already emitted as "title"; should not appear twice
        parsed = self._parsed(DATABASE_PAGE)
        assert list(parsed.keys()).count("title") == 1


# ---------------------------------------------------------------------------
# Tests: empty property values
# ---------------------------------------------------------------------------


class TestBuildFrontmatterEmptyProperties:
    def _parsed(self, page: dict) -> dict:
        import yaml

        result = build_frontmatter(page)
        inner = result.strip().lstrip("---").rstrip("---").strip()
        return yaml.safe_load(inner)

    def test_empty_select_is_null(self) -> None:
        parsed = self._parsed(PAGE_EMPTY_PROPERTIES)
        assert parsed["status"] is None

    def test_empty_multi_select_is_empty_list(self) -> None:
        parsed = self._parsed(PAGE_EMPTY_PROPERTIES)
        assert parsed["tags"] == []

    def test_empty_date_is_null(self) -> None:
        parsed = self._parsed(PAGE_EMPTY_PROPERTIES)
        assert parsed["due_date"] is None

    def test_empty_rich_text_is_null(self) -> None:
        parsed = self._parsed(PAGE_EMPTY_PROPERTIES)
        assert parsed["notes"] is None


# ---------------------------------------------------------------------------
# Tests: unsupported properties silently skipped
# ---------------------------------------------------------------------------


class TestInternalHelpers:
    """Coverage for edge-case branches in helper functions."""

    def test_plain_text_from_rich_text_type_text_fallback(self) -> None:
        """Handles chunk with type=text but no plain_text key."""
        from noteshift.frontmatter import _plain_text_from_rich_text

        chunks = [{"type": "text", "text": {"content": "hello"}}]
        assert _plain_text_from_rich_text(chunks) == "hello"

    def test_plain_text_from_rich_text_unknown_type_fallback(self) -> None:
        """Handles chunk with unknown type (neither plain_text nor text)."""
        from noteshift.frontmatter import _plain_text_from_rich_text

        chunks = [{"type": "equation", "equation": {"content": "E=mc²"}}]
        assert _plain_text_from_rich_text(chunks) == "E=mc²"

    def test_page_title_falls_back_to_untitled(self) -> None:
        """Returns 'Untitled' when no title property exists."""
        from noteshift.frontmatter import _page_title_from_properties

        assert _page_title_from_properties({}) == "Untitled"
        assert _page_title_from_properties({"Status": {"type": "select"}}) == "Untitled"

    def test_non_dict_property_value_skipped(self) -> None:
        """build_frontmatter skips properties whose value is not a dict."""
        import yaml

        page = {
            "id": "x",
            "properties": {
                "title": {
                    "type": "title",
                    "title": [{"plain_text": "T"}],
                },
                "bad_prop": "not-a-dict",
            },
        }
        result = build_frontmatter(page)
        inner = result.strip().lstrip("---").rstrip("---").strip()
        parsed = yaml.safe_load(inner)
        assert "bad_prop" not in parsed

    def test_extract_property_value_unknown_type_returns_none(self) -> None:
        """_extract_property_value returns None for unknown property types."""
        from noteshift.frontmatter import _extract_property_value

        assert _extract_property_value({"type": "people", "people": []}) is None


class TestBuildFrontmatterUnsupportedProperties:
    def _parsed(self, page: dict) -> dict:
        import yaml

        result = build_frontmatter(page)
        inner = result.strip().lstrip("---").rstrip("---").strip()
        return yaml.safe_load(inner)

    def test_people_property_skipped(self) -> None:
        parsed = self._parsed(PAGE_UNSUPPORTED_PROPERTIES)
        assert "assignee" not in parsed

    def test_relation_property_skipped(self) -> None:
        parsed = self._parsed(PAGE_UNSUPPORTED_PROPERTIES)
        assert "linked_pages" not in parsed

    def test_formula_property_skipped(self) -> None:
        parsed = self._parsed(PAGE_UNSUPPORTED_PROPERTIES)
        assert "formula_result" not in parsed

    def test_core_fields_still_present(self) -> None:
        parsed = self._parsed(PAGE_UNSUPPORTED_PROPERTIES)
        assert "notionId" in parsed
        assert "title" in parsed
