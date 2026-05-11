"""Comparison logic for flatdir entries."""

from __future__ import annotations
from enum import StrEnum

class status(StrEnum):
    """Status of an entry comparison."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"


def compare_entries(old_entries: list[dict[str, object]], new_entries: list[dict[str, object]]) -> list[dict[str, object]]:
    """Compare two lists of entries and return a flat list of affected items.
    
    Uses 'path' and 'name' as the unique key for comparison.
    Entries that have been added, modified, or removed are included.
    """
    old_map = {(str(e.get("path", ".")), str(e.get("name", ""))): e for e in old_entries}
    new_map = {(str(e.get("path", ".")), str(e.get("name", ""))): e for e in new_entries}
    
    changed: list[dict[str, object]] = []
    
    all_keys = set(old_map.keys()) | set(new_map.keys())
    
    for key in sorted(all_keys):
        old_item = old_map.get(key)
        new_item = new_map.get(key)
        
        if old_item is None:
            # Added
            changed.append({**new_item, "_status": status.ADDED})
        elif new_item is None:
            # Removed (since there's no new item, we include the old one)
            changed.append({**old_item, "_status": status.REMOVED})
        else:
            # Compare fields
            if old_item != new_item:
                # If any field has changed, add the new entry
                changed.append({**new_item, "_status": status.MODIFIED})
                    
    return changed
