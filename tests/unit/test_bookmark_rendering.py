from __future__ import annotations

from noteshift.exporter import _render_blocks


class _DummyClient:
    def list_block_children(self, _block_id: str):  # pragma: no cover
        return []


def test_bookmark_renders_as_link() -> None:
    blocks = [
        {
            "type": "bookmark",
            "bookmark": {"url": "https://example.com"},
            "has_children": False,
        }
    ]

    out = _render_blocks(_DummyClient(), blocks, indent="", page_map={})

    assert "[https://example.com](https://example.com)" in "\n".join(out)
