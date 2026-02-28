#!/usr/bin/env python3
"""Generate Notion test data for NoteShift export testing."""

import os
import sys

import httpx

NOTION_VERSION = "2025-09-03"


def main():
    token = os.getenv("NOTION_TOKEN")
    if not token:
        print("Error: Set NOTION_TOKEN env var")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    print("Searching for parent page...")
    with httpx.Client(timeout=30.0) as http:
        r = http.post(
            "https://api.notion.com/v1/search",
            headers=headers,
            json={"query": "", "page_size": 1},
        )
        r.raise_for_status()
        results = r.json().get("results", [])

    if not results:
        print("Error: No pages found")
        sys.exit(1)

    parent_id = results[0]["id"]
    print(f"Using parent: {parent_id}")

    print("\nCreating 'NoteShift Test Export'...")
    with httpx.Client(timeout=30.0) as http:
        r = http.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json={
                "parent": {"page_id": parent_id},
                "properties": {
                    "title": {"title": [{"text": {"content": "NoteShift Test Export"}}]}
                },
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"type": "text", "text": {"content": "Test with "}},
                                {
                                    "type": "text",
                                    "text": {"content": "bold"},
                                    "annotations": {"bold": True},
                                },
                                {"type": "text", "text": {"content": ", "}},
                                {
                                    "type": "text",
                                    "text": {"content": "italic"},
                                    "annotations": {"italic": True},
                                },
                                {"type": "text", "text": {"content": ", "}},
                                {
                                    "type": "text",
                                    "text": {"content": "code"},
                                    "annotations": {"code": True},
                                },
                            ]
                        },
                    },
                    {
                        "object": "block",
                        "type": "toggle",
                        "toggle": {
                            "rich_text": [
                                {"type": "text", "text": {"content": "Toggle"}}
                            ],
                            "children": [
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {"content": "Nested content"},
                                            }
                                        ]
                                    },
                                }
                            ],
                        },
                    },
                ],
            },
        )
        r.raise_for_status()
        root_id = r.json()["id"]

    print(f"Root: {root_id}")

    for i in range(1, 4):
        print(f"Creating Child Page {i}...")
        children = []
        if i == 1:
            children = [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {"type": "text", "text": {"content": f"Section {i}"}}
                        ]
                    },
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": f"Content for child {i}"}}
                        ]
                    },
                },
            ]
        with httpx.Client(timeout=30.0) as http:
            http.post(
                "https://api.notion.com/v1/pages",
                headers=headers,
                json={
                    "parent": {"page_id": root_id},
                    "properties": {
                        "title": {"title": [{"text": {"content": f"Child {i}"}}]}
                    },
                    "children": children,
                },
            ).raise_for_status()

    print("\nCreating database...")
    try:
        with httpx.Client(timeout=30.0) as http:
            r = http.post(
                "https://api.notion.com/v1/databases",
                headers=headers,
                json={
                    "parent": {"page_id": root_id},
                    "title": [{"text": {"content": "Test DB"}}],
                    "properties": {
                        "Name": {"title": {}},
                        "Status": {
                            "select": {
                                "options": [
                                    {"name": "Todo", "color": "red"},
                                    {"name": "Done", "color": "green"},
                                ]
                            }
                        },
                        "Tags": {
                            "multi_select": {
                                "options": [{"name": "bug"}, {"name": "feature"}]
                            }
                        },
                        "Count": {"number": {}},
                    },
                },
            )
            r.raise_for_status()
            db_id = r.json()["id"]
            print(f"DB: {db_id}")

        for i in range(1, 4):
            print(f"  Entry {i}...")
            with httpx.Client(timeout=30.0) as http:
                http.post(
                    "https://api.notion.com/v1/pages",
                    headers=headers,
                    json={
                        "parent": {"database_id": db_id},
                        "properties": {
                            "Name": {"title": [{"text": {"content": f"Item {i}"}}]},
                            "Status": {"select": {"name": "Todo"}},
                            "Tags": {"multi_select": [{"name": "feature"}]},
                            "Count": {"number": i * 10},
                        },
                    },
                ).raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"  Skipped database (requires integration capabilities): {e}")

    print("\nTest data ready!")
    print(f"Export: noteshift export --page-id {root_id}")


if __name__ == "__main__":
    main()
