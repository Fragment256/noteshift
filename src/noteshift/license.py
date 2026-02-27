"""License verification for NoteShift.

Free tier: max_depth = 2
Paid tier: unlimited depth
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def verify_license(key: str | None = None) -> dict:
    """Verify license and return feature limits.
    
    Args:
        key: License key. If None or invalid, returns free tier limits.
    
    Returns:
        dict with keys:
        - max_depth: int - maximum export depth (2 for free, 999 for paid)
        - features: list[str] - enabled features
    """
    # For MVP: DEMO key unlocks full access
    if key == "DEMO":
        return {
            "max_depth": 999,
            "features": ["unlimited_depth", "checkpoint_resume", "migration_reports"]
        }
    
    # Free tier
    return {
        "max_depth": 2,
        "features": []
    }


def check_depth_limit(current_depth: int, active_depth: int, has_license: bool) -> bool:
    """Check if children can be exported (would be at depth + 1).
    
    Args:
        current_depth: Current recursion depth (0-indexed from root)
        active_depth: Maximum allowed depth from license
        has_license: Whether user has a valid license
        
    Returns:
        True if export should proceed (children at depth+1), False if depth limit reached
    """
    if has_license:
        return True
    # Check if children (at depth + 1) would exceed limit
    return current_depth + 1 <= active_depth


def get_depth_warning(current_depth: int, max_depth: int) -> str | None:
    """Get warning message when depth limit is reached for children.
    
    Args:
        current_depth: Current recursion depth
        max_depth: Maximum allowed depth for this license tier
        
    Returns:
        Warning message if children would exceed limit, None otherwise
    """
    # Children of current level would be at depth + 1
    if current_depth + 1 > max_depth:
        return (
            f"[FREE] Depth limit ({max_depth}) reached at level {current_depth + 1}. "
            "Purchase a license for unlimited depth."
        )
    return None