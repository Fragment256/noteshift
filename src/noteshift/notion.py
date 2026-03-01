from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import httpx

NOTION_VERSION = "2025-09-03"


@dataclass(frozen=True)
class NotionClient:
    token: str

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def get_page(self, page_id: str) -> dict:
        with httpx.Client(timeout=30.0, headers=self._headers()) as client:
            r = client.get(f"https://api.notion.com/v1/pages/{page_id}")
            r.raise_for_status()
            return r.json()

    def list_block_children(self, block_id: str) -> list[dict]:
        """Return all children blocks for a block/page id (handles pagination)."""
        results: list[dict] = []
        cursor: str | None = None
        with httpx.Client(timeout=30.0, headers=self._headers()) as client:
            while True:
                params: dict[str, str | int] = {"page_size": 100}
                if cursor:
                    params["start_cursor"] = cursor
                url = f"https://api.notion.com/v1/blocks/{block_id}/children"
                r = client.get(url, params=params)
                r.raise_for_status()
                data = r.json()
                results.extend(data.get("results", []))
                if not data.get("has_more"):
                    break
                cursor = data.get("next_cursor")
        return results

    def get_data_source(self, data_source_id: str) -> dict:
        with httpx.Client(timeout=30.0, headers=self._headers()) as client:
            r = client.get(f"https://api.notion.com/v1/data_sources/{data_source_id}")
            r.raise_for_status()
            return r.json()

    def query_data_source(self, data_source_id: str) -> list[dict]:
        """Return all pages/rows in a data source (handles pagination)."""
        results: list[dict] = []
        cursor: str | None = None
        with httpx.Client(timeout=60.0, headers=self._headers()) as client:
            while True:
                payload: dict[str, object] = {"page_size": 100}
                if cursor:
                    payload["start_cursor"] = cursor
                url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
                r = client.post(url, json=payload)
                r.raise_for_status()
                data = r.json()
                results.extend(data.get("results", []))
                if not data.get("has_more"):
                    break
                cursor = data.get("next_cursor")
        return results

    def download_file(self, url: str, dest: Path) -> None:
        """Download a file from URL to destination path using httpx."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        with httpx.Client(timeout=60.0, follow_redirects=True) as client:
            r = client.get(url)
            r.raise_for_status()
            dest.write_bytes(r.content)
