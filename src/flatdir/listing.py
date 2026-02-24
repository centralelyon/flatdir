"""List entries in a directory and return metadata as a list of dict.

Each entry is a dict with keys determined by field plugins (defaults: name, type, mtime, size).
"""

from __future__ import annotations

import os
from pathlib import Path

from .plugins import defaults as _defaults
from .plugins_loader import load_fields_file

# built-in default fields, loaded once
DEFAULT_FIELDS = load_fields_file(_defaults.__file__)


def list_entries(
    root: Path,
    limit: int | None = None,
    depth: int | None = None,
    fields: dict[str, object] | None = None,
    exclude: list[tuple[str, str]] | None = None,
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    root = root.resolve()

    # merge default fields with custom fields (custom can override defaults)
    all_fields = dict(DEFAULT_FIELDS)
    if fields:
        all_fields.update(fields)

    for dirpath, dirnames, filenames in os.walk(root):
        base = Path(dirpath)
        # check depth constraint
        current_depth = len(base.relative_to(root).parts)
        if depth is not None and depth >= 0 and current_depth > depth:
            continue

        # list subdirectories at this level
        for dirname in dirnames:
            p = (base / dirname).resolve()
            entry: dict[str, object] = {}
            for field_name, func in all_fields.items():
                value = func(p, root)
                if value is not None:
                    entry[field_name] = value
            if _excluded(entry, exclude):
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
            if _excluded(entry, exclude):
                continue
            entries.append(entry)

    # return a sorted list of entries
    entries.sort(key=lambda e: str(e.get("name", "")))

    # apply limit if provided
    if limit is not None and limit >= 0:
        entries = entries[:limit]

    return entries


def _excluded(entry: dict[str, object], exclude: list[tuple[str, str]] | None) -> bool:
    """Return True if *entry* matches any of the exclude rules."""
    if not exclude:
        return False
    for field_name, value in exclude:
        if str(entry.get(field_name, "")) == value:
            return True
    return False
