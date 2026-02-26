"""List entries in a directory and return metadata as a list of dict.

Each entry is a dict with keys determined by field plugins (defaults: name, type, mtime, size).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from .plugins import defaults as _defaults
from .plugins_loader import load_fields_file

# built-in default fields, loaded once
DEFAULT_FIELDS = load_fields_file(_defaults.__file__)

IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".idea", ".vscode", ".ipynb_checkpoints", }
IGNORE_FILES = {".DS_Store", "Thumbs.db"}


def list_entries(
    root: Path,
    limit: int | None = None,
    depth: int | None = None,
    min_depth: int | None = None,
    add_depth: int | None = None,
    fields: dict[str, object] | None = None,
    exclude: list[tuple[str, str]] | None = None,
    only: list[tuple[str, str]] | None = None,
    add_fields: dict[str, object] | None = None,
    match: str | None = None,
    sort_by: str | None = None,
    sort_desc: bool = False,
    ignore_typical: bool = False,
    use_defaults: bool = True,
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    root = root.resolve()

    # merge default fields with custom fields (custom can override defaults)
    all_fields = dict(DEFAULT_FIELDS) if use_defaults else {}
    if fields:
        all_fields.update(fields)

    # compile regex pattern if match is provided
    pattern = None
    if match:
        pattern = re.compile(match)

    for dirpath, dirnames, filenames in os.walk(root):
        base = Path(dirpath)
        # check depth constraint
        current_depth = len(base.relative_to(root).parts)
        if depth is not None and depth >= 0 and current_depth > depth:
            continue

        if ignore_typical:
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.endswith(".egg-info")]
            filenames = [f for f in filenames if f not in IGNORE_FILES and not f.endswith(".pyc")]

        # list subdirectories at this level
        for dirname in dirnames:
            p = (base / dirname).resolve()
            entry: dict[str, object] = {}
            for field_name, func in all_fields.items():
                value = func(p, root)
                if value is not None:
                    entry[field_name] = value
            item_depth = current_depth + 1
            if add_fields and (add_depth is None or item_depth == add_depth):
                entry.update(add_fields)
            if _excluded(entry, exclude, p, root) or not _included(entry, only, p, root) or not _matched(entry, pattern, p, root):
                continue
            
            if min_depth is not None and min_depth > 0 and item_depth < min_depth:
                continue
                
            entries.append(entry)

        # list files at this level
        for filename in filenames:
            p = (base / filename).resolve()
            entry = {}
            for field_name, func in all_fields.items():
                value = func(p, root)
                if value is not None:
                    entry[field_name] = value
            item_depth = current_depth + 1
            if add_fields and (add_depth is None or item_depth == add_depth):
                entry.update(add_fields)
            if _excluded(entry, exclude, p, root) or not _included(entry, only, p, root) or not _matched(entry, pattern, p, root):
                continue

            if min_depth is not None and min_depth > 0 and item_depth < min_depth:
                continue

            entries.append(entry)

    # return a sorted list of entries
    sort_field = sort_by if sort_by else "name"

    def _get_sort_key(entry: dict[str, object]) -> tuple[int, object]:
        val = entry.get(sort_field)
        if val is None:
            return (0, "")
        if isinstance(val, (int, float)):
            return (1, val)
        return (2, str(val).lower())

    entries.sort(key=_get_sort_key, reverse=sort_desc)

    # apply limit if provided
    if limit is not None and limit >= 0:
        entries = entries[:limit]

    return entries


def _excluded(entry: dict[str, object], exclude: list[tuple[str, str]] | None, p: Path, root: Path) -> bool:
    """Return True if *entry* matches any of the exclude rules."""
    if not exclude:
        return False
    for field_name, value in exclude:
        entry_val = entry.get(field_name)
        if entry_val is None and field_name in _defaults.__dict__:
            func = getattr(_defaults, field_name)
            if callable(func):
                entry_val = func(p, root)
        if str(entry_val if entry_val is not None else "") == value:
            return True
    return False


def _included(entry: dict[str, object], only: list[tuple[str, str]] | None, p: Path, root: Path) -> bool:
    """Return True if *entry* matches the inclusive rules.
    If multiple fields are provided, it must match ALL fields (AND logic).
    If multiple values are provided for the same field, it must match ANY of them (OR logic).
    """
    if not only:
        return True
    
    # group by field
    required: dict[str, set[str]] = {}
    for f, v in only:
        required.setdefault(f, set()).add(v)
        
    for f, values in required.items():
        entry_val = entry.get(f)
        if entry_val is None and f in _defaults.__dict__:
            func = getattr(_defaults, f)
            if callable(func):
                entry_val = func(p, root)
        if str(entry_val if entry_val is not None else "") not in values:
            return False
            
    return True


def _matched(entry: dict[str, object], pattern: re.Pattern[str] | None, p: Path, root: Path) -> bool:
    """Return True if *entry* name matches the given regex pattern."""
    if pattern is None:
        return True
    name_val = entry.get("name")
    if name_val is None:
        name_val = _defaults.name(p, root)
    return pattern.search(str(name_val)) is not None
