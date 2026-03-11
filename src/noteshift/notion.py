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

    def get_database(self, database_id: str) -> dict:
        """Fetch a database schema (Notion "database" object).

        Note: In newer Notion API versions, databases expose one or more backing
        data sources via the `data_sources` field.
        """
        with httpx.Client(timeout=30.0, headers=self._headers()) as client:
            r = client.get(f"https://api.notion.com/v1/databases/{database_id}")
            r.raise_for_status()
            return r.json()

    def resolve_data_source_id(self, database_or_data_source_id: str) -> str:
        """Accept either a data_source_id or a database_id and return a data_source_id.

        Notion API v2025-09-03+ often returns child_database block IDs that are
        *database IDs*. Export queries must use /v1/data_sources/{id}/query,
        which requires the backing data_source_id.
        """
        with httpx.Client(timeout=30.0, headers=self._headers()) as client:
            # 1) Try treating it as a data source id
            r = client.get(
                f"https://api.notion.com/v1/data_sources/{database_or_data_source_id}"
            )
            if r.status_code == 200:
                return database_or_data_source_id

            # If not found, try treating it as a database id
            if r.status_code == 404:
                db = self.get_database(database_or_data_source_id)
                ds = db.get("data_sources") or []
                if not ds or not ds[0].get("id"):
                    raise RuntimeError(
                        "Database has no data_sources; cannot resolve data_source_id"
                    )

                # Notion databases can theoretically expose multiple backing
                # data sources. We currently pick the first one as the best
                # default.
                return str(ds[0]["id"])

            r.raise_for_status()
            # Unreachable, but keeps type checkers happy.
            return database_or_data_source_id

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
